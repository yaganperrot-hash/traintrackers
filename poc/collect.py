"""POC jalon 1 — collecte brute du flux temps réel SNCF.

Toutes les 2 min (rythme de rafraîchissement annoncé par la SNCF), télécharge :
  - GTFS-RT Trip Updates   (retards / suppressions, trains des 60 prochaines minutes)
  - GTFS-RT Service Alerts (perturbations au niveau du train)
et enregistre chaque réponse brute, compressée, dans poc/data/<flux>/<AAAA-MM-JJ>/<HHMMSS>.pb.gz.
Les Service Alerts ne sont enregistrées que si elles ont changé depuis le relevé précédent.
Le GTFS théorique (poc/data/gtfs/) est téléchargé une fois par jour.
Les fichiers de plus de --garder-jours jours sont effacés (défaut 7) ; le journal est plafonné.

Lancement :  python poc/collect.py            (Ctrl+C pour arrêter)
             python poc/collect.py --once     (un seul relevé, pour tester)
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import logging
import shutil
import time
from datetime import date, datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

PARIS = ZoneInfo("Europe/Paris")
DATA = Path(__file__).parent / "data"
INTERVALLE_S = 120
FLUX = {
    "trip_updates": "https://proxy.transport.data.gouv.fr/resource/sncf-gtfs-rt-trip-updates",
    "service_alerts": "https://proxy.transport.data.gouv.fr/resource/sncf-gtfs-rt-service-alerts",
}
SEULEMENT_SI_CHANGE = {"service_alerts"}
GTFS_URL = "https://eu.ftp.opendatasoft.com/sncf/plandata/Export_OpenData_SNCF_GTFS_NewTripId.zip"
HEADERS = {"User-Agent": "traintracker-poc/0.2", "Accept-Encoding": "gzip"}

log = logging.getLogger("collect")
_empreintes: dict[str, str] = {}


def telecharger_gtfs(client: httpx.Client) -> None:
    """Un GTFS théorique par jour (les horaires prévus changent)."""
    cible = DATA / "gtfs" / f"gtfs_{datetime.now(PARIS):%Y-%m-%d}.zip"
    if cible.exists():
        return
    cible.parent.mkdir(parents=True, exist_ok=True)
    log.info("Téléchargement du GTFS théorique…")
    r = client.get(GTFS_URL, timeout=300, follow_redirects=True)
    r.raise_for_status()
    cible.write_bytes(r.content)
    log.info("GTFS théorique : %s (%.1f Mo)", cible.name, len(r.content) / 1e6)


def derniere_empreinte(nom: str) -> str:
    fichiers = sorted((DATA / nom).glob("????-??-??/*.pb.gz"))
    if not fichiers:
        return ""
    try:
        return hashlib.sha256(gzip.decompress(fichiers[-1].read_bytes())).hexdigest()
    except Exception:
        return ""


def releve(client: httpx.Client) -> None:
    maintenant = datetime.now(PARIS)
    for nom, url in FLUX.items():
        try:
            r = client.get(url, timeout=60)
            r.raise_for_status()
            if not r.content:
                log.warning("%s : réponse 200 vide — traitée comme une panne", nom)
                continue
            if nom in SEULEMENT_SI_CHANGE:
                empreinte = hashlib.sha256(r.content).hexdigest()
                if nom not in _empreintes:  # après un redémarrage : comparer au dernier fichier stocké
                    _empreintes[nom] = derniere_empreinte(nom)
                if _empreintes[nom] == empreinte:
                    log.info("%s : inchangé, non stocké", nom)
                    continue
                _empreintes[nom] = empreinte
            dossier = DATA / nom / f"{maintenant:%Y-%m-%d}"
            dossier.mkdir(parents=True, exist_ok=True)
            fichier = dossier / f"{maintenant:%H%M%S}.pb.gz"
            fichier.write_bytes(gzip.compress(r.content, compresslevel=6))
            log.info("%s : %d o bruts → %d o stockés", nom, len(r.content), fichier.stat().st_size)
        except Exception as exc:  # un flux en panne ne doit pas faire perdre l'autre
            log.warning("%s : échec du relevé (%s)", nom, exc)


def purger(garder_jours: int) -> None:
    """Efface les dossiers de jours et les GTFS plus vieux que garder_jours."""
    limite = datetime.now(PARIS).date() - timedelta(days=garder_jours)
    for nom in FLUX:
        for d in (DATA / nom).glob("????-??-??"):
            try:
                if date.fromisoformat(d.name) < limite:
                    shutil.rmtree(d)
                    log.info("Purge : %s/%s", nom, d.name)
            except ValueError:
                continue
    for z in (DATA / "gtfs").glob("gtfs_????-??-??.zip"):
        try:
            if date.fromisoformat(z.stem[5:]) < limite:
                z.unlink()
                log.info("Purge : %s", z.name)
        except ValueError:
            continue


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="un seul relevé puis sortie")
    parser.add_argument("--garder-jours", type=int, default=7, help="jours de données brutes conservés")
    args = parser.parse_args()

    DATA.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(),
                  RotatingFileHandler(DATA / "collect.log", maxBytes=5_000_000, backupCount=2, encoding="utf-8")],
    )
    logging.Formatter.converter = lambda *_: datetime.now(PARIS).timetuple()  # heure de Paris, même sur un serveur en UTC
    logging.getLogger("httpx").setLevel(logging.WARNING)
    jour_traite = None
    with httpx.Client(headers=HEADERS) as client:
        while True:
            debut = time.monotonic()
            jour = datetime.now(PARIS).date()
            if jour != jour_traite:  # une fois au démarrage, puis à chaque changement de jour
                try:
                    telecharger_gtfs(client)
                    jour_traite = jour
                except Exception as exc:  # on réessaiera au prochain relevé
                    log.warning("GTFS théorique non téléchargé (%s)", exc)
                purger(args.garder_jours)
            releve(client)
            if args.once:
                break
            time.sleep(max(0.0, INTERVALLE_S - (time.monotonic() - debut)))


if __name__ == "__main__":
    main()
