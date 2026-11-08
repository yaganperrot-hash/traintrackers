"""Marques régionales des TER à garantie — ZONE CRITIQUE (alimente backend/regles.py).

Le GTFS SNCF ne porte ni la région ni la marque. La région calculée par majorité d'arrêts
(poc/regions.py) se trompe pour certaines lignes interrégionales : K2+ Paris–Montargis–Nevers est
attribuée à la Bourgogne-Franche-Comté alors qu'elle est un Rémi Express (Centre-Val de Loire).
On identifie donc la marque par la LIGNE (route_short_name + route_long_name du GTFS), et la ligne
fixe aussi la région. Le code seul ne suffit pas : « K2+ » existe en Normandie et en Centre-Val de Loire.

Sources (vérifiées le 2026-11-08, voir docs/regles-remboursement.md) :
  - Normandie : garantie des billets à réservation « Krono+ et Krono Paris/Normandie ».
  - Centre-Val de Loire : garantie Rémi Express sur Paris–Bourges, Tours–Orléans–Paris,
    Paris–Montargis–Nevers ; garantie Rémi (seuil 60 min) sur les autres trains Rémi.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from backend.regles import (CENTRE_VAL_DE_LOIRE, MARQUE_NOMAD_RESA, MARQUE_REMI,
                            MARQUE_REMI_EXPRESS, NORMANDIE)

SRC_NORMANDIE = "https://www.ter.sncf.com/normandie/services-contacts/sav/garantie-voyageurs-occasionnels"
SRC_REMI_EXPRESS = "https://www.ter.sncf.com/centre-val-de-loire/services-contacts/garantie-ponctualite-remi-express"


@dataclass(frozen=True)
class Identification:
    region: str | None
    marque: str | None
    a_confirmer: bool = False


def _norm(texte: str) -> str:
    t = unicodedata.normalize("NFD", texte or "")
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[\s\-–]+", " ", t).strip()


# (code de ligne, nom de ligne normalisé) → (marque, région, à confirmer)
LIGNES: dict[tuple[str, str], tuple[str, str, bool]] = {
    # Normandie — Krono+ (trains à réservation Paris–Normandie)
    ("K1+", _norm("Paris - Le Havre")): (MARQUE_NOMAD_RESA, NORMANDIE, False),
    ("K2+", _norm("Paris - Cherbourg")): (MARQUE_NOMAD_RESA, NORMANDIE, False),
    ("K21+", _norm("PARIS - CAEN")): (MARQUE_NOMAD_RESA, NORMANDIE, False),
    ("K3+", _norm("Paris - Deauville")): (MARQUE_NOMAD_RESA, NORMANDIE, False),
    # Centre-Val de Loire — Rémi Express (les trois axes de la garantie)
    ("K5+", _norm("Paris - Bourges - Nevers")): (MARQUE_REMI_EXPRESS, CENTRE_VAL_DE_LOIRE, False),
    ("K6+", _norm("Paris - Orléans - Tours")): (MARQUE_REMI_EXPRESS, CENTRE_VAL_DE_LOIRE, False),
    ("K8+", _norm("Paris - Orléans")): (MARQUE_REMI_EXPRESS, CENTRE_VAL_DE_LOIRE, False),
    ("K2+", _norm("Paris - Montargis - Nevers")): (MARQUE_REMI_EXPRESS, CENTRE_VAL_DE_LOIRE, False),
    # Tours–Orléans seul : couverture Rémi Express non confirmée → garantie Rémi (la plus basse).
    ("K16+", _norm("Tours-Blois-Orléans rapides")): (MARQUE_REMI, CENTRE_VAL_DE_LOIRE, True),
}
# Non retenu faute de preuve : K1 Paris–Dieppe (« Krono Paris/Normandie », réservation à vérifier).


def identifier(code_ligne: str, nom_ligne: str, region_calculee: str | None) -> Identification:
    """Région et marque d'un TER à partir de sa ligne GTFS et de la région calculée."""
    connue = LIGNES.get(((code_ligne or "").strip(), _norm(nom_ligne)))
    if connue:
        marque, region, a_confirmer = connue
        return Identification(region, marque, a_confirmer)
    if region_calculee == CENTRE_VAL_DE_LOIRE:
        return Identification(region_calculee, MARQUE_REMI)
    return Identification(region_calculee, None)
