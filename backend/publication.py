"""Post quotidien (jalon 4) : chiffres et textes à publier à la main sur X et Instagram.

Aucune règle ici : la liste des trains vient de l'API (/api/aujourdhui), qui calcule les droits avec
backend/regles.py. Ce module ne fait que compter, trier et rédiger. Les images sont dessinées par la
page frontend/publications.html à partir de ce que renvoie composer().
"""
from __future__ import annotations

import re
from datetime import date

ADRESSE = "monretard.fr"
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
        "novembre", "décembre"]
LIMITE_X = 280
LIMITE_INSTAGRAM = 2200


def date_longue(jour: date) -> str:
    return f"{JOURS[jour.weekday()]} {jour.day} {MOIS[jour.month - 1]}"


def date_courte(jour: date) -> str:
    return f"{JOURS[jour.weekday()][:3]}. {jour.day} {MOIS[jour.month - 1]}"


def duree(minutes: int) -> str:
    return f"+{minutes} min" if minutes < 60 else f"+{minutes // 60} h {minutes % 60:02d}"


def longueur_x(texte: str) -> int:
    """X compte une adresse comme 23 caractères, quelle que soit sa longueur."""
    return len(re.sub(r"\S+\.fr\S*", "x" * 23, texte))


def _quand(jour: date, aujourd_hui: date) -> str:
    ecart = (aujourd_hui - jour).days
    return "aujourd'hui" if ecart == 0 else "hier" if ecart == 1 else f"le {date_longue(jour).lower()}"


def _s(n: int) -> str:
    return "s" if n > 1 else ""


def _phrase_suppressions(n_sup: int, n_remb: int) -> str:
    """« Remboursement intégral » n'est affirmé que pour les trains dont c'est le droit calculé :
    un TER supprimé peut n'ouvrir qu'un bon d'achat (garanties régionales)."""
    if not n_sup:
        return ""
    base = f"{n_sup} train{_s(n_sup)} supprimé{_s(n_sup)}"
    if n_remb == n_sup:
        return f"{base} : remboursement intégral.\n"
    if n_remb:
        return f"{base}, dont {n_remb} avec remboursement intégral.\n"
    return f"{base}.\n"


def composer(jour: date, trains: list[dict], mis_a_jour: str | None, aujourd_hui: date) -> dict:
    """trains : ceux de /api/aujourdhui (ils ouvrent tous un droit).
    mis_a_jour : heure « HH:MM » du dernier relevé, affichée seulement pour le jour en cours."""
    liste = [{"prod": t["nom"], "num": t["numero"] or "", "route": f"{t['origine']} → {t['terminus']}",
              "r": t["retard_max_min"] or 0, "sup": bool(t["supprime"])} for t in trains]
    liste.sort(key=lambda t: (not t["sup"], -t["r"]))
    n = len(liste)
    n_sup = sum(t["sup"] for t in liste)
    n_remb = sum(1 for t in trains if t["supprime"] and (t.get("droit") or {}).get("statut") == "remboursement")
    pire = next((t for t in liste if not t["sup"]), None)
    quand = _quand(jour, aujourd_hui)
    long_ = date_longue(jour)

    if n == 0:
        x = (f"Aucun train ne t'ouvre de droit {quand}. Rare, profitons-en.\n"
             f"Un doute sur ton train ? → {ADRESSE}")
        instagram = (f"{long_} : aucun train ne t'ouvre de droit {quand}.\n\n"
                     f"Un doute sur ton train ? Vérifie-le sur {ADRESSE} (lien en bio).")
    else:
        accord = "nt" if n > 1 else ""
        x = (f"{n} train{_s(n)} t'ouvre{accord} un droit {quand}"
             + (f", dont {n_sup} supprimé{_s(n_sup)}" if n_sup else "") + ".\n"
             + (f"Le plus gros retard : {pire['prod']} {pire['num']}, {duree(pire['r'])}.\n" if pire else "")
             + f"Ton train est dedans ? → {ADRESSE}")
        instagram = (f"{long_} : {n} train{_s(n)} t'ouvre{accord} un droit.\n\n"
                     + (f"Le plus gros retard : {pire['prod']} {pire['num']} {pire['route']}, {duree(pire['r'])}.\n"
                        if pire else "")
                     + _phrase_suppressions(n_sup, n_remb)
                     + f"\nTon droit dépend du retard à ta gare d'arrivée. Vérifie ton train sur {ADRESSE} "
                       "(lien en bio).\n\n#train #retard #remboursement")

    arrete_a = None
    if mis_a_jour and jour == aujourd_hui:
        h, m = mis_a_jour.split(":")
        arrete_a = f"{int(h)} h" if m == "00" else f"{int(h)} h {m}"
    return {"jour": jour.isoformat(), "date_longue": long_, "date_courte": date_courte(jour), "quand": quand,
            "arrete_a": arrete_a, "adresse": ADRESSE, "n": n, "n_supprimes": n_sup, "pire": pire, "trains": liste,
            "textes": {"x": x, "instagram": instagram},
            "longueurs": {"x": longueur_x(x), "x_max": LIMITE_X,
                          "instagram": len(instagram), "instagram_max": LIMITE_INSTAGRAM}}
