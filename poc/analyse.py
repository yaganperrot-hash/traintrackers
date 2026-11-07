"""POC jalon 1 — analyse des relevés collectés par poc/collect.py.

Pour chaque jour de relevés, répond aux questions du risque principal :
  - le retard au terminus est-il fourni, et suivi jusqu'à l'arrivée ? stable ?
  - les suppressions (train entier / arrêts sautés) sont-elles signalées ?
  - couverture par produit (OUI, OGO, IC, TER, LYR…) : trains vus en temps réel / trains prévus au GTFS
  - volume stocké par jour

Lancement :  python poc/analyse.py              (tous les jours collectés)
             python poc/analyse.py 2026-11-08   (un jour)
Le rapport est affiché et écrit dans poc/data/rapport_<AAAA-MM-JJ>.md.
"""
from __future__ import annotations

import csv
import gzip
import io
import re
import sys
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from google.transit import gtfs_realtime_pb2 as rt

PARIS = ZoneInfo("Europe/Paris")
DATA = Path(__file__).parent / "data"
CANCELED = rt.TripDescriptor.CANCELED
SKIPPED = rt.TripUpdate.StopTimeUpdate.SKIPPED
SEUILS_MIN = (30, 60, 120, 180)
TOLERANCE_ARRIVEE_S = 5 * 60  # « suivi jusqu'à l'arrivée » = vu à moins de 5 min de l'arrivée estimée


def produit(trip_id: str) -> str:
    m = re.search(r"F\d+_F:([A-Z0-9]+):", trip_id) or re.search(r":([A-Z]{2,4}):FR:", trip_id)
    return m.group(1) if m else "?"


@dataclass
class Suivi:
    produit: str
    nb_releves: int = 0
    supprime: bool = False
    arrets_sautes: bool = False
    terminus: str | None = None
    retards_terminus: list[int] = field(default_factory=list)  # secondes, dans l'ordre des relevés
    arrivee_estimee: int | None = None  # epoch, dernière valeur vue
    dernier_releve: int = 0  # epoch du dernier relevé où le train apparaît


def charger_gtfs() -> tuple[dict[str, str], dict[str, set[str]]]:
    """trip_id → service_id, et service_id → dates (AAAAMMJJ) de circulation."""
    zips = sorted((DATA / "gtfs").glob("gtfs_*.zip"))
    if not zips:
        return {}, {}
    with zipfile.ZipFile(zips[-1]) as z:
        def lire(nom: str):
            return csv.DictReader(io.TextIOWrapper(z.open(nom), encoding="utf-8-sig"))
        trips = {r["trip_id"]: r["service_id"] for r in lire("trips.txt")}
        dates: dict[str, set[str]] = defaultdict(set)
        for r in lire("calendar_dates.txt"):
            if r["exception_type"] == "1":
                dates[r["service_id"]].add(r["date"])
    return trips, dates


def analyser_jour(jour: str, trips: dict[str, str], dates: dict[str, set[str]]) -> str:
    fichiers = sorted((DATA / "trip_updates" / jour).glob("*.pb.gz"))
    suivis: dict[tuple[str, str], Suivi] = {}
    erreurs = 0
    for f in fichiers:
        msg = rt.FeedMessage()
        try:
            msg.ParseFromString(gzip.decompress(f.read_bytes()))
        except Exception:
            erreurs += 1
            continue
        ts = msg.header.timestamp
        for e in msg.entity:
            if not e.HasField("trip_update"):
                continue
            tu = e.trip_update
            cle = (tu.trip.trip_id, tu.trip.start_date)
            s = suivis.setdefault(cle, Suivi(produit(tu.trip.trip_id)))
            s.nb_releves += 1
            s.dernier_releve = ts
            if tu.trip.schedule_relationship == CANCELED:
                s.supprime = True
            if any(st.schedule_relationship == SKIPPED for st in tu.stop_time_update):
                s.arrets_sautes = True
            if tu.stop_time_update:
                der = tu.stop_time_update[-1]
                if der.arrival.HasField("delay"):
                    s.terminus = der.stop_id
                    s.retards_terminus.append(der.arrival.delay)
                    s.arrivee_estimee = der.arrival.time or s.arrivee_estimee

    # Ne garder que les trains partis ce jour-là (un relevé voit aussi la veille et le lendemain).
    du_jour = {k: v for k, v in suivis.items() if k[1] == jour.replace("-", "")}

    par_prod: dict[str, Counter] = defaultdict(Counter)
    instables = []
    suspects = []
    for (tid, _), s in du_jour.items():
        c = par_prod[s.produit]
        c["vus"] += 1
        c["supprimes"] += s.supprime
        c["arrets_sautes"] += s.arrets_sautes and not s.supprime
        if s.retards_terminus and not s.supprime:
            c["avec_retard_terminus"] += 1
            final = s.retards_terminus[-1]
            if s.arrivee_estimee and s.dernier_releve >= s.arrivee_estimee - TOLERANCE_ARRIVEE_S:
                c["suivis_jusqu_arrivee"] += 1
            for seuil in SEUILS_MIN:
                if final >= seuil * 60:
                    c[f">={seuil}"] += 1
            ecart = max(s.retards_terminus) - min(s.retards_terminus)
            if ecart >= 15 * 60:
                instables.append((tid, s.produit, s.retards_terminus[0] // 60, final // 60, ecart // 60))
            if final >= 180 * 60:
                suspects.append((tid, s.produit, final // 60, s.terminus))

    prevus = Counter()
    d = jour.replace("-", "")
    for tid, svc in trips.items():
        if d in dates.get(svc, ()):
            prevus[produit(tid)] += 1

    volume = {
        nom: sum(f.stat().st_size for f in (DATA / nom / jour).glob("*.pb.gz"))
        for nom in ("trip_updates", "service_alerts")
    }

    lignes = [
        f"# Rapport POC — {jour}",
        "",
        f"- Relevés Trip Updates : {len(fichiers)} (illisibles : {erreurs})",
        f"- Volume stocké : " + ", ".join(f"{k} {v / 1e6:.1f} Mo" for k, v in volume.items()),
        f"- Trains distincts du jour vus en temps réel : {len(du_jour)}",
        "",
        "## Par produit",
        "",
        "| Produit | Prévus GTFS | Vus TR | Couverture | Supprimés | Arrêts sautés | Retard terminus fourni "
        "| Suivis jusqu'à l'arrivée | ≥30 | ≥60 | ≥120 | ≥180 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for p in sorted(set(par_prod) | set(prevus), key=lambda p: -prevus.get(p, 0)):
        c = par_prod.get(p, Counter())
        couv = f"{c['vus'] / prevus[p]:.0%}" if prevus.get(p) else "—"
        lignes.append(
            f"| {p} | {prevus.get(p, 0)} | {c['vus']} | {couv} | {c['supprimes']} | {c['arrets_sautes']} "
            f"| {c['avec_retard_terminus']} | {c['suivis_jusqu_arrivee']} | "
            + " | ".join(str(c[f'>={s}']) for s in SEUILS_MIN) + " |"
        )
    lignes += [
        "",
        "Note : « Vus TR » ne compte que les trains apparus dans le flux (fenêtre de 60 min avant passage).",
        "Un train à l'heure peut ne jamais y figurer : la couverture mesure la présence, pas la fiabilité.",
        "",
        f"## Retards au terminus instables (écart ≥ 15 min entre relevés) : {len(instables)}",
        "",
    ]
    lignes += [f"- {p} {tid[:40]}… : {a} → {b} min (écart {e})" for tid, p, a, b, e in instables[:20]]
    lignes += ["", f"## Retards ≥ 3 h au terminus (à vérifier, possibles artefacts) : {len(suspects)}", ""]
    lignes += [f"- {p} {tid[:40]}… : {m} min à {t}" for tid, p, m, t in suspects[:20]]
    return "\n".join(lignes) + "\n"


def main() -> None:
    jours = sys.argv[1:] or sorted(p.name for p in (DATA / "trip_updates").iterdir() if p.is_dir())
    trips, dates = charger_gtfs()
    for jour in jours:
        rapport = analyser_jour(jour, trips, dates)
        (DATA / f"rapport_{jour}.md").write_text(rapport, encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
        print(rapport)


if __name__ == "__main__":
    main()
