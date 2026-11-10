"""Lecture du flux temps réel SNCF (GTFS-RT) — fonctions pures, sans base de données.

Un relevé Trip Updates devient une liste d'`Observation` : un train un jour donné, et ce qu'on
sait de lui à chaque gare. Un relevé Service Alerts devient un dictionnaire numéro de train → cause.
On garde des FAITS (retards, suppressions) ; les droits sont calculés à l'affichage (backend/regles.py).
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from datetime import date

from google.transit import gtfs_realtime_pb2 as rt

from backend.regles import PRODUITS_HORS_PERIMETRE

CANCELED = rt.TripDescriptor.CANCELED
SKIPPED = rt.TripUpdate.StopTimeUpdate.SKIPPED


def produit(trip_id: str) -> str:
    """Code produit du trip_id (OUI, OGO, IC, TER…). Repris de poc/analyse.py.

    Circulations ajoutées hors GTFS (« OCESN<numéro><F|R> ») : produit déduit du numéro —
    HYPOTHÈSE constatée le 2026-11-07, non documentée par la SNCF.
    """
    m = re.search(r"F\d+_F:([A-Z0-9]+):", trip_id) or re.search(r":([A-Z]{2,4}):FR:", trip_id)
    if m:
        return m.group(1)
    m = re.match(r"OCESN(\d+)([FR])", trip_id)
    if not m:
        return "?"
    num, mode = m.groups()
    if mode == "R":
        return "CAR*"
    if len(num) == 6 and num[0] == "1":
        return "TRANSILIEN*"
    if len(num) == 6 and num[0] == "8":
        return "TER*"
    if len(num) == 4:
        return "IC*"
    return "?"


def numero(trip_id: str) -> str | None:
    """Numéro commercial du train : « OCESN9253F1187_F:… » → « 9253 »."""
    m = re.match(r"OCESN(\d+)[FR]", trip_id)
    return m.group(1) if m else None


def uic(stop_id: str) -> str | None:
    """Code UIC de la gare : « StopPoint:OCETGV INOUI-87686006 » → « 87686006 »."""
    m = re.search(r"(\d{8})$", stop_id or "")
    return m.group(1) if m else None


@dataclass
class Passage:
    gare: str              # code UIC
    ordre: int             # position dans le relevé (0 = origine)
    arrivee_prevue: int | None  # epoch, horaire théorique (estimée − retard)
    retard_s: int | None   # retard à l'arrivée annoncé, en secondes
    saute: bool = False    # arrêt supprimé


@dataclass
class Observation:
    trip_id: str
    jour: date
    numero: str | None
    produit: str
    supprimee: bool
    depart_prevu: int | None       # epoch, départ théorique de la première gare
    passages: list[Passage] = field(default_factory=list)


def lire_trip_updates(contenu: bytes) -> tuple[int, list[Observation]]:
    """(horodatage du relevé, observations des trains dans le périmètre)."""
    msg = rt.FeedMessage()
    msg.ParseFromString(contenu)
    obs: list[Observation] = []
    for e in msg.entity:
        if not e.HasField("trip_update"):
            continue
        tu = e.trip_update
        tid = tu.trip.trip_id
        prod = produit(tid)
        if prod in PRODUITS_HORS_PERIMETRE:
            continue
        try:
            jour = date(int(tu.trip.start_date[:4]), int(tu.trip.start_date[4:6]), int(tu.trip.start_date[6:8]))
        except (ValueError, IndexError):
            continue
        o = Observation(tid, jour, numero(tid), prod, tu.trip.schedule_relationship == CANCELED, None)
        for i, st in enumerate(tu.stop_time_update):
            g = uic(st.stop_id)
            if not g:
                continue
            if i == 0 and st.departure.time:
                o.depart_prevu = st.departure.time - st.departure.delay
            a = st.arrival if st.HasField("arrival") else None
            o.passages.append(Passage(
                gare=g, ordre=i,
                arrivee_prevue=(a.time - a.delay) if a is not None and a.time else None,
                retard_s=a.delay if a is not None and a.HasField("delay") else None,
                saute=st.schedule_relationship == SKIPPED,
            ))
        obs.append(o)
    return msg.header.timestamp, obs


# Titres d'alerte qui n'apprennent rien sur la cause : on prend alors la description.
_TITRES_VIDES = {"plus d'information", "plus d'informations", "retard", "information", "informations"}


def _texte_fr(ts) -> str:
    t = next((x.text for x in ts.translation if x.language == "fr"), "")
    return t or (ts.translation[0].text if ts.translation else "")


def nettoyer(texte: str) -> str:
    """Texte d'alerte sans HTML ni espaces superflus, coupé à 300 caractères."""
    t = html.unescape(re.sub(r"<[^>]+>", " ", texte or ""))
    t = re.sub(r"\s+", " ", t.replace("\xa0", " ")).strip()
    return t[:300]


def lire_alertes(contenu: bytes) -> dict[str, str]:
    """Numéro de train → cause annoncée (texte de la dernière alerte qui le cite)."""
    msg = rt.FeedMessage()
    msg.ParseFromString(contenu)
    causes: dict[str, str] = {}
    for e in msg.entity:
        if not e.HasField("alert"):
            continue
        al = e.alert
        titre = nettoyer(_texte_fr(al.header_text)).rstrip(" :.")
        texte = titre if titre.lower() not in _TITRES_VIDES else nettoyer(_texte_fr(al.description_text))
        if not texte:
            continue
        for ie in al.informed_entity:
            n = numero(ie.trip.trip_id) if ie.trip.trip_id else None
            if n:
                causes[n] = texte
    return causes
