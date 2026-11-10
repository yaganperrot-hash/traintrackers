"""Ingestion : relevés bruts de la collecte (poc/data/) → base de données.

Toutes les 30 s, traite dans l'ordre chaque relevé Trip Updates pas encore noté dans `collectes`,
avec la dernière alerte connue à cette heure-là. Rejouable : les fichiers bruts restent 7 jours,
et une annonce plus ancienne n'écrase jamais une plus récente.

Lancement : python -m backend.ingestion          (boucle)
            python -m backend.ingestion --once   (traite ce qui attend, puis sort)
Variables : DATABASE_URL (obligatoire), DONNEES (défaut : poc/data)
"""
from __future__ import annotations

import argparse
import asyncio
import bisect
import gzip
import logging
import os
import time
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from backend import base
from backend.flux import Observation, lire_alertes, lire_trip_updates
from backend.referentiel import Referentiel, Regions

PARIS = ZoneInfo("Europe/Paris")
DONNEES = Path(os.environ.get("DONNEES", Path(__file__).resolve().parents[1] / "poc" / "data"))
PAUSE_S = 30
AGE_MIN_S = 5  # un fichier plus récent peut être en cours d'écriture

log = logging.getLogger("ingestion")


def cle(chemin: Path) -> str:
    """« AAAA-MM-JJ/HHMMSS » : ordre chronologique des relevés."""
    return f"{chemin.parent.name}/{chemin.name.split('.')[0]}"


class Ingestion:
    def __init__(self, engine, donnees: Path = DONNEES) -> None:
        self.engine = engine
        self.donnees = donnees
        self.regions = Regions()
        self.ref: Referentiel | None = None
        self.ref_zip: Path | None = None
        self.traites: set[str] | None = None
        self.vus: dict[tuple, tuple] = {}  # (jour, trip_id, gare) → dernière valeur écrite

    def _gtfs_pour(self, jour: str) -> Path | None:
        zips = sorted((self.donnees / "gtfs").glob("gtfs_????-??-??.zip"))
        avant = [z for z in zips if z.stem[5:] <= jour]
        return (avant or zips or [None])[-1]

    async def _referentiel(self, jour: str) -> Referentiel | None:
        z = self._gtfs_pour(jour)
        if z is None:
            return None
        if z != self.ref_zip:
            log.info("Référentiel : %s", z.name)
            self.ref = Referentiel.depuis_gtfs(z, self.regions)
            self.ref_zip = z
            async with self.engine.begin() as cx:
                await base.ecrire_gares(cx, [g.__dict__ for g in self.ref.gares.values()])
        return self.ref

    def _alerte_pour(self, k: str) -> Path | None:
        fichiers = sorted((self.donnees / "service_alerts").glob("????-??-??/*.pb.gz"), key=cle)
        cles = [cle(f) for f in fichiers]
        i = bisect.bisect_right(cles, k)
        return fichiers[i - 1] if i else None

    def _lignes(self, ref: Referentiel | None, obs: list[Observation], ts: int) -> list[dict]:
        quand = base.horodatage(ts)
        lignes = []
        for o in obs:
            gs = [p.gare for p in o.passages]
            region, marque, a_confirmer = ref.region_et_marque(o.produit, o.trip_id, gs) if ref else (None, None, False)
            ligne = ref.lignes.get(o.trip_id) if ref else None
            lignes.append({
                "jour": o.jour, "trip_id": o.trip_id, "numero": o.numero, "produit": o.produit,
                "ligne_code": ligne.code if ligne else None, "ligne_nom": ligne.nom if ligne else None,
                "region": region, "marque": marque, "marque_a_confirmer": a_confirmer,
                "origine": gs[0] if gs else None, "terminus": gs[-1] if gs else None,
                "depart_prevu": base.horodatage(o.depart_prevu), "supprimee": o.supprimee,
                "premiere_annonce": quand, "derniere_annonce": quand,
            })
        return lignes

    async def traiter(self, chemin: Path) -> int:
        k = cle(chemin)
        ts, obs = lire_trip_updates(gzip.decompress(chemin.read_bytes()))
        ref = await self._referentiel(chemin.parent.name)
        alerte = self._alerte_pour(k)
        causes = lire_alertes(gzip.decompress(alerte.read_bytes())) if alerte else {}
        quand = base.horodatage(ts)
        async with self.engine.begin() as cx:
            ids = await base.ecrire_circulations(cx, self._lignes(ref, obs, ts)) if obs else {}
            a_ecrire, a_causer = [], []
            for o in obs:
                cid = ids.get((o.jour, o.trip_id))
                if cid is None:
                    continue
                if o.numero in causes and self.vus.get((o.jour, o.trip_id, "cause")) != causes[o.numero]:
                    a_causer.append({"id": cid, "cause": causes[o.numero]})
                    self.vus[(o.jour, o.trip_id, "cause")] = causes[o.numero]
                for p in o.passages:
                    valeur = (p.ordre, p.arrivee_prevue, p.retard_s, p.saute)
                    if self.vus.get((o.jour, o.trip_id, p.gare)) == valeur:
                        continue
                    self.vus[(o.jour, o.trip_id, p.gare)] = valeur
                    a_ecrire.append({"circulation_id": cid, "gare": p.gare, "ordre": p.ordre,
                                     "arrivee_prevue": base.horodatage(p.arrivee_prevue),
                                     "retard_s": p.retard_s, "saute": p.saute, "annonce_le": quand})
            await base.ecrire_causes(cx, a_causer)
            await base.ecrire_passages(cx, a_ecrire)
            await base.noter_collecte(cx, f"trip_updates/{k}.pb.gz", quand, len(obs))
        return len(obs)

    def _oublier_vieux(self) -> None:
        limite = date.fromordinal(datetime.now(PARIS).date().toordinal() - 2)
        self.vus = {c: v for c, v in self.vus.items() if c[0] >= limite}

    async def tour(self) -> int:
        if self.traites is None:
            async with self.engine.connect() as cx:
                self.traites = await base.deja_traite(cx)
        maintenant = time.time()
        a_faire = sorted(
            (f for f in (self.donnees / "trip_updates").glob("????-??-??/*.pb.gz")
             if f"trip_updates/{cle(f)}.pb.gz" not in self.traites and maintenant - f.stat().st_mtime > AGE_MIN_S),
            key=cle)
        for f in a_faire:
            nom = f"trip_updates/{cle(f)}.pb.gz"
            debut = time.monotonic()
            try:
                n = await self.traiter(f)
                log.info("%s : %d trains (%.1f s)", nom, n, time.monotonic() - debut)
            except Exception as exc:  # un fichier illisible ne bloque pas les suivants
                log.exception("%s : échec", nom)
                async with self.engine.begin() as cx:
                    await base.noter_collecte(cx, nom, None, None, f"{type(exc).__name__}: {exc}"[:500])
            self.traites.add(nom)
        self._oublier_vieux()
        return len(a_faire)


async def principal(une_fois: bool) -> None:
    engine = base.moteur()
    await base.creer_schema(engine)
    ing = Ingestion(engine)
    try:
        while True:
            await ing.tour()
            if une_fois:
                break
            await asyncio.sleep(PAUSE_S)
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.Formatter.converter = lambda *_: datetime.now(PARIS).timetuple()
    asyncio.run(principal(args.once))


if __name__ == "__main__":
    main()
