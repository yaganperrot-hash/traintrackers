"""Tests de l'identification des marques régionales (backend/marques.py)."""
import csv
import glob
import io
import zipfile
from pathlib import Path

import pytest

from backend import regles as R
from backend.marques import LIGNES, _norm, identifier

CVL, NOR, BFC = "Centre-Val de Loire", "Normandie", "Bourgogne-Franche-Comté"


@pytest.mark.parametrize("code,nom,region_calculee,region,marque", [
    ("K1+", "Paris - Le Havre", NOR, NOR, R.MARQUE_NOMAD_RESA),
    ("K2+", "Paris - Cherbourg", NOR, NOR, R.MARQUE_NOMAD_RESA),
    ("K21+", "PARIS - CAEN", NOR, NOR, R.MARQUE_NOMAD_RESA),
    ("K3+", "Paris - Deauville", NOR, NOR, R.MARQUE_NOMAD_RESA),
    ("K5+", "Paris - Bourges - Nevers", CVL, CVL, R.MARQUE_REMI_EXPRESS),
    ("K6+", "Paris - Orléans - Tours", CVL, CVL, R.MARQUE_REMI_EXPRESS),
    ("K8+", "Paris - Orléans", CVL, CVL, R.MARQUE_REMI_EXPRESS),
    # Région calculée fausse (majorité d'arrêts en BFC) : la ligne la corrige.
    ("K2+", "Paris - Montargis - Nevers", BFC, CVL, R.MARQUE_REMI_EXPRESS),
])
def test_lignes_a_garantie(code, nom, region_calculee, region, marque):
    i = identifier(code, nom, region_calculee)
    assert (i.region, i.marque, i.a_confirmer) == (region, marque, False)


def test_meme_code_deux_regions():
    assert identifier("K2+", "Paris - Cherbourg", NOR).marque == R.MARQUE_NOMAD_RESA
    assert identifier("K2+", "Paris - Montargis - Nevers", BFC).marque == R.MARQUE_REMI_EXPRESS


def test_k16_plus_prudent_en_remi():
    i = identifier("K16+", "Tours-Blois-Orléans rapides", CVL)
    assert i.marque == R.MARQUE_REMI and i.a_confirmer


def test_autres_ter_cvl_sont_remi():
    assert identifier("C11", "Orléans - Tours", CVL).marque == R.MARQUE_REMI


def test_paris_dieppe_non_retenu():
    assert identifier("K1", "Paris - Dieppe", NOR).marque is None


def test_autres_regions_sans_marque():
    i = identifier("C30", "Saint-Étienne - Roanne", "Auvergne-Rhône-Alpes")
    assert (i.region, i.marque) == ("Auvergne-Rhône-Alpes", None)


def test_nom_insensible_casse_accents_tirets():
    assert identifier("K6+", "paris – orleans  -  tours", None).marque == R.MARQUE_REMI_EXPRESS


def test_chaine_complete_k2_montargis_ouvre_droit():
    i = identifier("K2+", "Paris - Montargis - Nevers", BFC)
    assert R.evaluer("TER", 45, region=i.region, marque=i.marque).eligible


# Garde-fou : chaque ligne de la table existe encore dans le dernier GTFS téléchargé (poc/data, non
# versionné). Si la SNCF renomme une ligne, ce test le signale au lieu de perdre la garantie en silence.
GTFS = sorted(glob.glob(str(Path(__file__).parents[1] / "poc" / "data" / "gtfs" / "gtfs_*.zip")))


@pytest.mark.skipif(not GTFS, reason="pas de GTFS local")
def test_table_presente_dans_le_gtfs():
    with zipfile.ZipFile(GTFS[-1]) as z:
        lignes = {(r["route_short_name"].strip(), _norm(r["route_long_name"]))
                  for r in csv.DictReader(io.TextIOWrapper(z.open("routes.txt"), encoding="utf-8-sig"))}
    absentes = [k for k in LIGNES if k not in lignes]
    assert not absentes, f"lignes introuvables dans le GTFS : {absentes}"
