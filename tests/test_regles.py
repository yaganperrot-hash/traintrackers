"""Tests des règles d'éligibilité (backend/regles.py) — chaque seuil testé à la minute près."""
import pytest

from backend import regles as R
from backend.regles import Statut, evaluer

BAREMES = [R.G30, R.G30_INTERNATIONAL, R.OUIGO, R.TRENITALIA, R.EUROSTAR, R.PLANCHER_UE,
           R.NOMAD_RESA, R.REMI_EXPRESS]


# --- Invariants des barèmes ------------------------------------------------------------------
@pytest.mark.parametrize("b", BAREMES, ids=lambda b: b.regle)
def test_paliers_strictement_croissants(b):
    seuils = [s for s, _ in b.paliers]
    pcts = [p for _, p in b.paliers]
    assert seuils == sorted(set(seuils))
    assert pcts == sorted(pcts)
    assert all(0 < p <= 100 for p in pcts)


@pytest.mark.parametrize("b", BAREMES, ids=lambda b: b.regle)
def test_chaque_bareme_cite_sa_source(b):
    assert b.source and b.source.startswith("https://")


def test_produits_sans_regle_identifiee_sont_a_confirmer():
    for produit in ("ICE", "TRN"):
        assert evaluer(produit, 120).a_confirmer


# --- G30 : TGV INOUI, Intercités -------------------------------------------------------------
@pytest.mark.parametrize("produit", ["OUI", "IC", "ICN", "IC*"])
@pytest.mark.parametrize("retard,pct,forme", [
    (29, None, None), (30, 25, "bon d'achat"), (59, 25, "bon d'achat"), (60, 25, "virement"),
    (119, 25, "virement"), (120, 50, "virement"), (179, 50, "virement"), (180, 75, "virement"),
    (400, 75, "virement"),
])
def test_g30(produit, retard, pct, forme):
    d = evaluer(produit, retard)
    assert d.pourcentage == pct
    assert d.forme == forme
    assert d.statut == (Statut.DROIT if pct else Statut.AUCUN)
    assert d.lien == R.LIEN_G30


@pytest.mark.parametrize("retard,pct", [(29, None), (30, 25), (119, 25), (120, 50), (180, 50), (600, 50)])
def test_g30_international_plafonne_a_50(retard, pct):
    assert evaluer("LYR", retard).pourcentage == pct


# --- OUIGO : automatique, dès 60 min ---------------------------------------------------------
@pytest.mark.parametrize("retard,pct", [(30, None), (59, None), (60, 25), (119, 25), (120, 50), (300, 50)])
def test_ouigo(retard, pct):
    d = evaluer("OGO", retard)
    assert d.pourcentage == pct
    assert d.statut == (Statut.AUTOMATIQUE if pct else Statut.AUCUN)


def test_ouigo_automatique_dit_rien_a_faire():
    assert "Rien à faire" in evaluer("OGO", 90).message


# --- Autres opérateurs -----------------------------------------------------------------------
@pytest.mark.parametrize("retard,pct,forme", [(29, None, None), (30, 25, "bon d'achat"), (60, 25, None), (120, 50, None)])
def test_trenitalia(retard, pct, forme):
    d = evaluer("TRENITALIA", retard)
    assert (d.pourcentage, d.forme) == (pct, forme)


@pytest.mark.parametrize("produit", ["EUROSTAR", "ICE", "TRN"])
@pytest.mark.parametrize("retard,pct", [(59, None), (60, 25), (119, 25), (120, 50)])
def test_seuil_60_min(produit, retard, pct):
    assert evaluer(produit, retard).pourcentage == pct


# --- Suppressions grandes lignes -------------------------------------------------------------
@pytest.mark.parametrize("produit", ["OUI", "IC", "LYR", "OGO", "ICE"])
def test_suppression_donne_droit_au_remboursement(produit):
    d = evaluer(produit, supprime=True)
    assert d.statut == Statut.REMBOURSEMENT
    assert d.eligible


def test_suppression_ouigo_renvoie_vers_ouigo():
    assert evaluer("OGO", supprime=True).lien == R.LIEN_OUIGO


# --- TER par région --------------------------------------------------------------------------
@pytest.mark.parametrize("region", ["Auvergne-Rhône-Alpes", "Bourgogne-Franche-Comté", "Bretagne",
                                    "Hauts-de-France", "Nouvelle-Aquitaine", "Provence-Alpes-Côte d'Azur",
                                    "Occitanie"])
def test_ter_sans_garantie_occasionnels(region):
    for supprime in (False, True):
        d = evaluer("TER", 90, supprime=supprime, region=region)
        assert d.statut == Statut.AUCUN
        assert not d.eligible
        assert "pas de remboursement par train" in d.message


def test_ter_occitanie_mentionne_la_correspondance():
    assert "correspondance" in evaluer("TER", 90, region="Occitanie").message


def test_ter_grand_est_cas_par_cas():
    assert evaluer("TER", 45, region="Grand Est").statut == Statut.CAS_PAR_CAS


@pytest.mark.parametrize("retard,pct", [(29, None), (30, 25), (120, 50), (180, 75)])
def test_ter_normandie_nomad_resa(retard, pct):
    d = evaluer("TER", retard, region="Normandie", marque=R.MARQUE_NOMAD_RESA)
    assert d.pourcentage == pct
    assert d.a_confirmer


def test_ter_normandie_hors_nomad_resa_sans_garantie():
    assert evaluer("TER", 90, region="Normandie").statut == Statut.AUCUN


def test_ter_normandie_nomad_resa_supprime():
    assert evaluer("TER", supprime=True, region="Normandie", marque=R.MARQUE_NOMAD_RESA).eligible


@pytest.mark.parametrize("retard,pct", [(29, None), (30, 25), (120, 50), (180, 75)])
def test_ter_remi_express(retard, pct):
    assert evaluer("TER", retard, region="Centre-Val de Loire", marque=R.MARQUE_REMI_EXPRESS).pourcentage == pct


def test_ter_remi_des_60_min_sans_bareme_invente():
    assert not evaluer("TER", 59, region="Centre-Val de Loire", marque=R.MARQUE_REMI).eligible
    d = evaluer("TER", 60, region="Centre-Val de Loire", marque=R.MARQUE_REMI)
    assert d.eligible and d.pourcentage is None and d.a_confirmer


def test_ter_pays_de_la_loire_suppression_seulement():
    assert evaluer("TER", supprime=True, region="Pays de la Loire").pourcentage == 100
    assert not evaluer("TER", 90, region="Pays de la Loire").eligible


@pytest.mark.parametrize("produit", ["TT", "NAV", "TER*"])
def test_tram_train_et_navettes_suivent_la_regle_ter(produit):
    assert evaluer(produit, 90, region="Bretagne").regle == "TER_SANS_GARANTIE"


# --- Hors périmètre / inconnu ----------------------------------------------------------------
@pytest.mark.parametrize("produit", ["TRANSILIEN*", "CTE", "CAR*", "CRE"])
def test_hors_perimetre(produit):
    assert evaluer(produit, 200).statut == Statut.HORS_PERIMETRE


def test_produit_inconnu_ne_promet_rien():
    d = evaluer("XYZ", 200)
    assert not d.eligible and d.a_confirmer
