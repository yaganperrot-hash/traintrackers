"""Référentiel tiré du GTFS théorique SNCF : gares (nom, région, position) et lignes des trains.

Région d'une gare : point-dans-polygone sur les contours des régions (backend/ref/regions.geojson,
france-geojson, version simplifiée ; repris de poc/regions.py).
Région d'un TER : région majoritaire parmi ses gares hors Île-de-France, puis corrigée par la ligne
(backend/marques.py), qui fixe aussi la marque des TER à garantie.
"""
from __future__ import annotations

import csv
import io
import json
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from backend.marques import identifier
from backend.regles import PRODUITS_TER

REGIONS_GEOJSON = Path(__file__).parent / "ref" / "regions.geojson"
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
            if x0 <= lon <= x1 and y0 <= lat <= y1 and any(
                    _dans_anneau(lon, lat, p[0]) and not any(_dans_anneau(lon, lat, t) for t in p[1:])
                    for p in polys):
                return nom
        return None  # hors France métropolitaine


@dataclass(frozen=True)
class Gare:
    uic: str
    nom: str
    region: str | None
    lat: float
    lon: float


@dataclass(frozen=True)
class Ligne:
    code: str
    nom: str


class Referentiel:
    def __init__(self, gares: dict[str, Gare], lignes: dict[str, Ligne]) -> None:
        self.gares = gares    # UIC → Gare
        self.lignes = lignes  # trip_id → Ligne

    @classmethod
    def depuis_gtfs(cls, chemin_zip: Path, regions: Regions | None = None) -> "Referentiel":
        regions = regions or Regions()
        with zipfile.ZipFile(chemin_zip) as z:
            def lire(nom: str):
                return csv.DictReader(io.TextIOWrapper(z.open(nom), encoding="utf-8-sig"))
            gares: dict[str, Gare] = {}
            for s in lire("stops.txt"):
                if not s["stop_id"].startswith("StopArea:") or not s["stop_lat"]:
                    continue
                code = s["stop_id"][-8:]
                lat, lon = float(s["stop_lat"]), float(s["stop_lon"])
                gares[code] = Gare(code, s["stop_name"], regions.de(lon, lat), lat, lon)
            routes = {r["route_id"]: Ligne(r["route_short_name"], r["route_long_name"]) for r in lire("routes.txt")}
            lignes = {t["trip_id"]: routes[t["route_id"]] for t in lire("trips.txt") if t["route_id"] in routes}
        return cls(gares, lignes)

    def region_et_marque(self, produit: str, trip_id: str, gares: list[str]) -> tuple[str | None, str | None, bool]:
        """(région, marque, à confirmer) — seulement pour les TER, sinon (None, None, False)."""
        if produit not in PRODUITS_TER:
            return None, None, False
        c = Counter(self.gares[g].region for g in gares if g in self.gares and self.gares[g].region)
        hors_idf = Counter({r: n for r, n in c.items() if r != ILE_DE_FRANCE})
        calculee = (hors_idf or c).most_common(1)[0][0] if c else None
        ligne = self.lignes.get(trip_id)
        ident = identifier(ligne.code if ligne else "", ligne.nom if ligne else "", calculee)
        return ident.region, ident.marque, ident.a_confirmer
