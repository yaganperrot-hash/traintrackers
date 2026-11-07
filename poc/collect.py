"""POC jalon 1 — collecte brute du flux temps réel SNCF.

Toutes les 2 min (rythme de rafraîchissement annoncé par la SNCF), télécharge :
  - GTFS-RT Trip Updates   (retards / suppressions, trains des 60 prochaines minutes)
  - GTFS-RT Service Alerts (perturbations au niveau du train)
et enregistre chaque réponse brute, compressée, dans poc/data/<flux>/<AAAA-MM-JJ>/<HHMMSS>.pb.gz.
Au démarrage, télécharge une fois le GTFS théorique (poc/data/gtfs/) s'il est absent.

Lancement :  python poc/collect.py            (Ctrl+C pour arrêter)
             python poc/collect.py --once     (un seul relevé, pour tester)
"""
from __future__ import annotations

import argparse
import gzip
import logging
import time
from datetime import datetime
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
GTFS_URL = "https://eu.ftp.opendatasoft.com/sncf/plandata/Export_OpenData_SNCF_GTFS_NewTripId.zip"
HEADERS = {"User-Agent": "traintracker-poc/0.1", "Accept-Encoding": "gzip"}

log = logging.getLogger("collect")


def telecharger_gtfs(client: httpx.Client) -> None:
    cible = DATA / "gtfs" / f"gtfs_{datetime.now(PARIS):%Y-%m-%d}.zip"
    if any((DATA / "gtfs").glob("gtfs_*.zip")):
        return
    cible.parent.mkdir(parents=True, exist_ok=True)
    log.info("Téléchargement du GTFS théorique…")
    r = client.get(GTFS_URL, timeout=300, follow_redirects=True)
    r.raise_for_status()
    cible.write_bytes(r.content)
    log.info("GTFS théorique : %s (%.1f Mo)", cible.name, len(r.content) / 1e6)


def releve(client: httpx.Client) -> None:
    maintenant = datetime.now(PARIS)
    for nom, url in FLUX.items():
        try:
            r = client.get(url, timeout=60)
            r.raise_for_status()
            if not r.content:
                log.warning("%s : réponse 200 vide — traitée comme une panne", nom)
                continue
            dossier = DATA / nom / f"{maintenant:%Y-%m-%d}"
            dossier.mkdir(parents=True, exist_ok=True)
            fichier = dossier / f"{maintenant:%H%M%S}.pb.gz"
            fichier.write_bytes(gzip.compress(r.content, compresslevel=6))
            log.info("%s : %d o bruts → %d o stockés", nom, len(r.content), fichier.stat().st_size)
        except Exception as exc:  # un flux en panne ne doit pas faire perdre l'autre
            log.warning("%s : échec du relevé (%s)", nom, exc)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="un seul relevé puis sortie")
    args = parser.parse_args()

    DATA.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(DATA / "collect.log", encoding="utf-8")],
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    with httpx.Client(headers=HEADERS) as client:
        try:
            telecharger_gtfs(client)
        except Exception as exc:
            log.warning("GTFS théorique non téléchargé (%s) — l'analyse de couverture en aura besoin", exc)
        while True:
            debut = time.monotonic()
            releve(client)
            if args.once:
                break
            time.sleep(max(0.0, INTERVALLE_S - (time.monotonic() - debut)))


if __name__ == "__main__":
    main()
