"""POC jalon 2 — rattacher chaque gare et chaque TER à sa région.

Le GTFS SNCF ne porte ni la région ni la marque régionale (vérifié le 2026-11-07). On déduit :
  - la région d'une gare : point-dans-polygone sur les contours des régions
    (france-geojson, version simplifiée, téléchargée dans poc/data/ref/regions.geojson) ;
  - la région d'un TER : région majoritaire parmi ses arrêts, hors Île-de-France
    (beaucoup de TER finissent à Paris sans être organisés par l'Île-de-France).

Lancement : python poc/regions.py   → bilan + poc/data/ref/ter_regions.json (trip_id → région)
"""
from __future__ import annotations

import csv
import io
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

DATA = Path(__file__).parent / "data"
REGIONS_GEOJSON = DATA / "ref" / "regions.geojson"
ILE_DE_FRANCE = "Île-de-France"


def _dans_anneau(x: float, y: float, anneau: list[list[float]]) -> bool:
    dedans = False
    j = len(anneau) - 1
    for i in range(len(anneau)):
        xi, yi = anneau[i][0], anneau[i][1]
        xj, yj = anneau[j][0], anneau[j][1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            dedans = not dedans
        j = i
    return dedans


def _dans_polygone(x: float, y: float, polygone: list) -> bool:
    # polygone = [anneau extérieur, trous…]
    return _dans_anneau(x, y, polygone[0]) and not any(_dans_anneau(x, y, t) for t in polygone[1:])


class Regions:
    def __init__(self, chemin: Path = REGIONS_GEOJSON) -> None:
        geo = json.loads(chemin.read_text(encoding="utf-8"))
        self.zones = []
        for f in geo["features"]:
            g = f["geometry"]
            polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
            xs = [p[0] for poly in polys for p in poly[0]]
            ys = [p[1] for poly in polys for p in poly[0]]
            self.zones.append((f["properties"]["nom"], polys, (min(xs), min(ys), max(xs), max(ys))))

    def de(self, lon: float, lat: float) -> str | None:
        for nom, polys, (x0, y0, x1, y1) in self.zones:
            if x0 <= lon <= x1 and y0 <= lat <= y1 and any(_dans_polygone(lon, lat, p) for p in polys):
                return nom
        return None  # hors France métropolitaine (Suisse, Belgique, Italie…)


def construire() -> dict[str, str]:
    regions = Regions()
    zips = sorted((DATA / "gtfs").glob("gtfs_*.zip"))
    with zipfile.ZipFile(zips[-1]) as z:
        def lire(nom: str):
            return csv.DictReader(io.TextIOWrapper(z.open(nom), encoding="utf-8-sig"))
        region_arret = {
            s["stop_id"]: regions.de(float(s["stop_lon"]), float(s["stop_lat"]))
            for s in lire("stops.txt") if s["stop_lat"] and s["stop_lon"]
        }
        ter = {t["trip_id"] for t in lire("trips.txt") if ":TER:" in t["trip_id"]}
        compte: dict[str, Counter] = {}
        for st in lire("stop_times.txt"):
            if st["trip_id"] in ter:
                r = region_arret.get(st["stop_id"])
                if r:
                    compte.setdefault(st["trip_id"], Counter())[r] += 1
    resultat = {}
    for tid, c in compte.items():
        hors_idf = Counter({r: n for r, n in c.items() if r != ILE_DE_FRANCE})
        resultat[tid] = (hors_idf or c).most_common(1)[0][0]
    sans = sum(1 for r in region_arret.values() if r is None)
    print(f"Arrêts : {len(region_arret)} (hors France métropolitaine : {sans})")
    print(f"TER rattachés : {len(resultat)} / {len(ter)}")
    for r, n in Counter(resultat.values()).most_common():
        print(f"  {r} : {n}")
    return resultat


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    resultat = construire()
    (DATA / "ref" / "ter_regions.json").write_text(json.dumps(resultat, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
