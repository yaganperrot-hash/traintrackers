"""Règles d'éligibilité au remboursement — ZONE CRITIQUE.

Source unique : docs/regles-remboursement.md (validé le 2026-11-07). Toute modification ici doit
d'abord y être documentée avec sa source, puis validée.

Principes :
  - on n'invente aucun barème : une valeur inconnue reste `None` et la règle est `a_confirmer` ;
  - en cas de doute sur un train ferroviaire international, on applique le plancher légal européen
    (règlement UE 2021/782, art. 19) marqué `a_confirmer` — jamais plus ;
  - le retard passé à `evaluer` est celui à la gare d'arrivée du voyageur (ou le maximum constaté
    sur le parcours pour le post quotidien, avec la mention « selon ta gare d'arrivée ») ;
  - on n'affiche que des pourcentages : le prix du billet est inconnu.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Statut(str, Enum):
    DROIT = "droit"                # le voyageur peut demander une indemnisation
    AUTOMATIQUE = "automatique"    # indemnisation versée sans démarche (OUIGO)
    REMBOURSEMENT = "remboursement"  # train supprimé : remboursement du billet à demander
    AUCUN = "aucun"                # pas de droit (sous le seuil, ou pas de garantie)
    CAS_PAR_CAS = "cas_par_cas"    # réclamation examinée au cas par cas
    HORS_PERIMETRE = "hors_perimetre"  # Transilien, cars : non suivis


@dataclass(frozen=True)
class Droit:
    statut: Statut
    regle: str                 # identifiant de la règle appliquée
    message: str               # texte affiché (site / post)
    pourcentage: int | None = None  # % du prix du billet
    forme: str | None = None   # « bon d'achat », « virement », …
    lien: str | None = None    # où faire la demande / se renseigner
    a_confirmer: bool = False  # règle non confirmée sur une source officielle
    source: str | None = None

    @property
    def eligible(self) -> bool:
        return self.statut in (Statut.DROIT, Statut.AUTOMATIQUE, Statut.REMBOURSEMENT)


@dataclass(frozen=True)
class Bareme:
    regle: str
    nom: str
    paliers: tuple[tuple[int, int], ...]  # (seuil en minutes, % du billet), croissants
    lien: str | None
    source: str
    a_confirmer: bool = False

    def pourcentage(self, retard_min: int) -> int | None:
        pct = None
        for seuil, p in self.paliers:
            if retard_min >= seuil:
                pct = p
        return pct

    @property
    def seuil(self) -> int:
        return self.paliers[0][0]


# --- Liens et sources (docs/regles-remboursement.md) -----------------------------------------
LIEN_G30 = "https://www.sncf-voyageurs.com/fr/contactez-nous/demande-et-reclamation/?path=%2FTR&stepCode=TR_D1"
LIEN_OUIGO = "https://www.ouigo.com/contact"
LIEN_TRENITALIA = "https://trenitalia.fr/informations/faire-une-demande-indemnisation/"
LIEN_EUROSTAR = "https://www.eurostar.com/fr-fr/voyage/informations-trafic/politique-de-compensation"
LIEN_DB = "https://int.bahn.de/fr/aide/contact/formulaires"
LIEN_TER = "https://www.sncf-voyageurs.com/fr/contactez-nous/en-cas-de-retard/ter-transilien/"
SRC_SNCF_CONNECT = "https://www.sncf-connect.com/aide/retard-de-votre-train-et-remboursement"
SRC_UE = "https://eur-lex.europa.eu/legal-content/FR/TXT/HTML/?uri=CELEX:32021R0782"
SRC_OUIGO = "https://cdn-fr.ouigo.com/edito-p-v3-assets/2026-03/24-03-2026_CGTV%20V71%20OUIGO.pdf"

# --- Barèmes ---------------------------------------------------------------------------------
G30 = Bareme("G30", "Garantie G30", ((30, 25), (120, 50), (180, 75)), LIEN_G30, SRC_SNCF_CONNECT)
G30_INTERNATIONAL = Bareme("G30_INT", "Garantie G30 (international)", ((30, 25), (120, 50)),
                           LIEN_G30, SRC_SNCF_CONNECT)
OUIGO = Bareme("OUIGO", "OUIGO", ((60, 25), (120, 50)), LIEN_OUIGO, SRC_OUIGO)
TRENITALIA = Bareme("TRENITALIA", "Trenitalia France", ((30, 25), (120, 50)), LIEN_TRENITALIA,
                    "https://trenitalia.fr/assistance/vos-droits-en-cas-de-retard/")
EUROSTAR = Bareme("EUROSTAR", "Eurostar", ((60, 25), (120, 50)), LIEN_EUROSTAR, LIEN_EUROSTAR)
PLANCHER_UE = Bareme("UE", "Règlement européen 2021/782", ((60, 25), (120, 50)), None, SRC_UE,
                     a_confirmer=True)
NOMAD_RESA = Bareme(
    "TER_NORMANDIE_NOMAD_RESA", "Garantie Nomad Résa", ((30, 25), (120, 50), (180, 75)),
    "https://www.ter.sncf.com/normandie/services-contacts/sav/garantie-voyageurs-occasionnels",
    "https://www.ter.sncf.com/normandie/services-contacts/sav/garantie-voyageurs-occasionnels",
    a_confirmer=True)
REMI_EXPRESS = Bareme(
    "TER_CVL_REMI_EXPRESS", "Garantie Rémi Express", ((30, 25), (120, 50), (180, 75)),
    "https://www.ter.sncf.com/centre-val-de-loire/services-contacts/garantie-ponctualite-remi-express",
    "https://www.ter.sncf.com/centre-val-de-loire/services-contacts/garantie-ponctualite-remi-express",
    a_confirmer=True)

# Produit (code du trip_id du flux SNCF) → barème. Les TER sont traités à part (par région).
BAREME_PAR_PRODUIT: dict[str, Bareme] = {
    "OUI": G30, "IC": G30, "ICN": G30, "IC*": G30,
    "LYR": G30_INTERNATIONAL,
    "OGO": OUIGO,
    "TRENITALIA": TRENITALIA,  # absent du flux SNCF au 2026-11-07
    "EUROSTAR": EUROSTAR,      # absent du flux SNCF au 2026-11-07
    # Règle non identifiée → plancher européen, à confirmer :
    "ICE": PLANCHER_UE,        # ICE France–Allemagne : G30 internationale ou règles DB ?
    "TRN": PLANCHER_UE,        # Paris–Bruxelles, produit non identifié
}
PRODUITS_TER = {"TER", "TER*", "TT", "NAV"}
PRODUITS_HORS_PERIMETRE = {"TRANSILIEN*", "CTE", "CAR*", "CRE"}

NORMANDIE = "Normandie"
CENTRE_VAL_DE_LOIRE = "Centre-Val de Loire"
PAYS_DE_LA_LOIRE = "Pays de la Loire"
OCCITANIE = "Occitanie"
GRAND_EST = "Grand Est"
MARQUE_NOMAD_RESA = "NOMAD_RESA"
MARQUE_REMI_EXPRESS = "REMI_EXPRESS"
MARQUE_REMI = "REMI"


def _depuis_bareme(b: Bareme, retard_min: int) -> Droit:
    pct = b.pourcentage(retard_min)
    if pct is None:
        return Droit(Statut.AUCUN, b.regle,
                     f"Moins de {b.seuil} min de retard : pas d'indemnisation ({b.nom} dès {b.seuil} min).",
                     lien=b.lien, a_confirmer=b.a_confirmer, source=b.source)
    if b is OUIGO:
        return Droit(Statut.AUTOMATIQUE, b.regle,
                     f"OUIGO : {pct} % du billet, versé automatiquement. Rien à faire : OUIGO t'écrit. "
                     "Pas reçu sous 15 jours ? Contacte OUIGO.",
                     pourcentage=pct, forme="bon d'achat (remboursable)", lien=b.lien, source=b.source)
    forme = None
    if b in (G30, G30_INTERNATIONAL):
        forme = "bon d'achat" if retard_min < 60 else "virement"
    elif b is TRENITALIA and retard_min < 60:
        forme = "bon d'achat"
    elif b in (NOMAD_RESA, REMI_EXPRESS):
        forme = "bon d'achat"
    precision = " (règle à confirmer)" if b.a_confirmer else ""
    texte_forme = f" en {forme}" if forme else ""
    return Droit(Statut.DROIT, b.regle,
                 f"{b.nom} : {pct} % du prix du billet{texte_forme}, selon ta gare d'arrivée{precision}.",
                 pourcentage=pct, forme=forme, lien=b.lien, a_confirmer=b.a_confirmer, source=b.source)


def _suppression_grandes_lignes(produit: str) -> Droit:
    lien = LIEN_OUIGO if produit == "OGO" else LIEN_G30
    return Droit(Statut.REMBOURSEMENT, "SUPPRESSION",
                 "Train supprimé : tu peux demander le remboursement intégral de ton billet. "
                 "Si tu as pris un autre train, ton droit dépend de ton retard à l'arrivée.",
                 pourcentage=100, lien=lien, a_confirmer=True, source=SRC_UE)


def _ter(retard_min: int | None, supprime: bool, region: str | None, marque: str | None) -> Droit:
    nom = f"TER {region}" if region else "TER"
    if region == NORMANDIE and marque == MARQUE_NOMAD_RESA:
        if supprime:
            return Droit(Statut.DROIT, NOMAD_RESA.regle,
                         "Train Nomad Résa supprimé sans préavis : indemnisation possible en bon d'achat "
                         "(règle à confirmer).", forme="bon d'achat", lien=NOMAD_RESA.lien,
                         a_confirmer=True, source=NOMAD_RESA.source)
        return _depuis_bareme(NOMAD_RESA, retard_min or 0)
    if region == CENTRE_VAL_DE_LOIRE and marque == MARQUE_REMI_EXPRESS and not supprime:
        return _depuis_bareme(REMI_EXPRESS, retard_min or 0)
    if region == CENTRE_VAL_DE_LOIRE and marque == MARQUE_REMI and not supprime:
        if (retard_min or 0) >= 60:
            return Droit(Statut.DROIT, "TER_CVL_REMI",
                         "Rémi : indemnisation en bon d'achat à partir de 60 min de retard "
                         "(barème à confirmer).", forme="bon d'achat", lien=REMI_EXPRESS.lien,
                         a_confirmer=True, source=REMI_EXPRESS.source)
    if region == PAYS_DE_LA_LOIRE and supprime:
        return Droit(Statut.DROIT, "TER_PDL_SUPPRESSION",
                     "Train Aléop supprimé sans solution de remplacement dans les 30 min : 100 % du billet "
                     "en bon d'achat Aléop, à demander sous 30 jours (règle à confirmer).",
                     pourcentage=100, forme="bon d'achat",
                     lien="https://www.ter.sncf.com/pays-de-la-loire/services-contacts/garantie-ponctualite-occasionnels",
                     a_confirmer=True,
                     source="https://www.ter.sncf.com/pays-de-la-loire/services-contacts/garantie-ponctualite-occasionnels")
    if region == GRAND_EST:
        return Droit(Statut.CAS_PAR_CAS, "TER_GRAND_EST",
                     f"{nom} : pas de barème, mais une réclamation au service client est examinée au cas par cas.",
                     lien="https://www.ter.sncf.com/grand-est/services-contacts/questions-reponses",
                     a_confirmer=True)
    complement = (" Avec une correspondance (billet unique) et 60 min de retard ou plus, une indemnisation "
                  "est possible.") if region == OCCITANIE else ""
    etat = "supprimé" if supprime else "en retard"
    return Droit(Statut.AUCUN, "TER_SANS_GARANTIE",
                 f"{nom} {etat} : pas de remboursement par train pour un billet à l'unité.{complement} "
                 "Abonné ? Ta région prévoit peut-être une compensation mensuelle.",
                 lien=LIEN_TER, a_confirmer=True)


def evaluer(produit: str, retard_min: int | None = None, supprime: bool = False,
            region: str | None = None, marque: str | None = None) -> Droit:
    """Droit d'un voyageur pour un train donné.

    produit    : code du flux (OUI, OGO, IC, LYR, TER…, voir poc/analyse.py:produit)
    retard_min : retard à la gare d'arrivée du voyageur, en minutes (ignoré si supprimé)
    supprime   : train supprimé
    region     : région du TER (poc/regions.py), ignorée hors TER
    marque     : NOMAD_RESA, REMI_EXPRESS, REMI pour les TER à garantie
    """
    if produit in PRODUITS_HORS_PERIMETRE:
        return Droit(Statut.HORS_PERIMETRE, "HORS_PERIMETRE",
                     "Ce service (Transilien, car) n'est pas suivi.")
    if produit in PRODUITS_TER:
        return _ter(retard_min, supprime, region, marque)
    bareme = BAREME_PAR_PRODUIT.get(produit)
    if supprime:
        return _suppression_grandes_lignes(produit)
    if bareme is None:
        return Droit(Statut.AUCUN, "INCONNU",
                     "Type de train non identifié : nous ne pouvons pas indiquer tes droits.", a_confirmer=True)
    return _depuis_bareme(bareme, retard_min or 0)
