"""API du site + pages (frontend/). Les droits sont calculés ici, à la lecture, par backend/regles.py.

Lancement : uvicorn backend.api:app   (DATABASE_URL obligatoire)
"""
from __future__ import annotations

import time
from contextlib import asynccontextmanager
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select

from backend import base
from backend import regles as R
from backend.publication import composer
from backend.regles import Droit, Statut, evaluer

PARIS = ZoneInfo("Europe/Paris")
FRONTEND = Path(__file__).resolve().parents[1] / "frontend"
CACHE_S = 60

NOMS = {"OUI": "TGV INOUI", "OGO": "OUIGO", "IC": "Intercités", "IC*": "Intercités", "ICN": "Intercités de nuit",
        "LYR": "Lyria", "ICE": "ICE", "TER": "TER", "TER*": "TER", "TT": "Tram-train", "NAV": "Navette",
        "TRN": "Trenitalia"}
NOMS_MARQUE = {"NOMAD_RESA": "TER Krono+", "REMI_EXPRESS": "Rémi Express", "REMI": "Rémi"}
NOMS_REGLE = {b.regle: b.nom for b in (R.G30, R.G30_INTERNATIONAL, R.OUIGO, R.TRENITALIA, R.EUROSTAR,
                                        R.PLANCHER_UE, R.NOMAD_RESA, R.REMI_EXPRESS)}
NOMS_REGLE.update({"SUPPRESSION": "Train supprimé", "TER_CVL_REMI": "Rémi (Centre-Val de Loire)",
                   "TER_PDL_SUPPRESSION": "Aléop (Pays de la Loire)", "TER_GRAND_EST": "TER Grand Est",
                   "TER_SANS_GARANTIE": "TER", "INCONNU": "Type de train inconnu"})


def nom_train(produit: str, marque: str | None) -> str:
    return NOMS_MARQUE.get(marque or "") or NOMS.get(produit, produit)


def heure(dt: datetime | None) -> str | None:
    return dt.astimezone(PARIS).strftime("%H:%M") if dt else None


def droit_json(d: Droit) -> dict:
    return {"statut": d.statut.value, "regle": d.regle, "regle_nom": NOMS_REGLE.get(d.regle, d.regle), "message": d.message, "pourcentage": d.pourcentage,
            "forme": d.forme, "lien": d.lien, "a_confirmer": d.a_confirmer, "source": d.source}


def droit_a(c, retard_s: int | None) -> Droit:
    if c.produit == "?":
        # Type de train inconnu (circulation ajoutée hors GTFS) : aucun droit affirmé, même supprimé.
        # evaluer() renverrait « remboursement » pour une suppression avant de vérifier le produit.
        return evaluer(c.produit)
    return evaluer(c.produit, None if retard_s is None else max(0, retard_s) // 60, c.supprimee, c.region, c.marque)


@asynccontextmanager
async def cycle(app: FastAPI):
    app.state.engine = base.moteur()
    app.state.cache = {}
    yield
    await app.state.engine.dispose()


app = FastAPI(title="monretard.fr", lifespan=cycle, docs_url=None, redoc_url=None)


async def _gares(cx, uics: set[str]) -> dict[str, str]:
    if not uics:
        return {}
    res = await cx.execute(select(base.gares.c.uic, base.gares.c.nom).where(base.gares.c.uic.in_(uics)))
    return {u: n for u, n in res.all()}


@app.get("/api/aujourdhui")
async def aujourdhui(jour: date | None = None):
    """Trains du jour qui ouvrent un droit à au moins une gare (ou supprimés avec droit)."""
    jour = jour or datetime.now(PARIS).date()
    cle = ("aujourdhui", jour)
    cache = app.state.cache.get(cle)
    if cache and time.monotonic() - cache[0] < CACHE_S:
        return cache[1]
    c_, p_ = base.circulations.c, base.passages.c
    async with app.state.engine.connect() as cx:
        circs = (await cx.execute(select(base.circulations).where(c_.jour == jour))).all()
        retards: dict[int, list[int]] = {}
        terminus: dict[int, int | None] = {}
        par_id = {c.id: c for c in circs}
        res = await cx.execute(select(p_.circulation_id, p_.gare, p_.retard_s, p_.saute)
                               .where(p_.circulation_id.in_(select(c_.id).where(c_.jour == jour))))
        for cid, gare, retard_s, saute in res.all():
            if retard_s is not None and not saute:
                retards.setdefault(cid, []).append(retard_s)
            if gare == par_id[cid].terminus:
                terminus[cid] = retard_s
        maj = (await cx.execute(select(func.max(base.collectes.c.releve_le)))).scalar()
        trains = []
        for c in circs:
            if c.supprimee:
                d = droit_a(c, None)
            else:
                rs = retards.get(c.id) or []
                d = droit_a(c, max(rs)) if rs else None
            if d is None or not d.eligible:
                continue
            trains.append({"numero": c.numero, "produit": c.produit, "nom": nom_train(c.produit, c.marque),
                           "origine": c.origine, "terminus": c.terminus, "depart": heure(c.depart_prevu),
                           "supprime": c.supprimee, "cause": c.cause,
                           "retard_max_min": None if c.supprimee else max(retards.get(c.id) or [0]) // 60,
                           "retard_terminus_min": None if terminus.get(c.id) is None else terminus[c.id] // 60,
                           "droit": droit_json(d)})
        noms = await _gares(cx, {t["origine"] for t in trains} | {t["terminus"] for t in trains})
    for t in trains:
        t["origine"], t["terminus"] = noms.get(t["origine"], t["origine"]), noms.get(t["terminus"], t["terminus"])
    trains.sort(key=lambda t: (not t["supprime"], -(t["retard_max_min"] or 0)))
    reponse = {"jour": jour.isoformat(), "mis_a_jour": heure(maj), "trains": trains}
    app.state.cache[cle] = (time.monotonic(), reponse)
    return reponse


@app.get("/api/publication")
async def publication(jour: date | None = None):
    """Post quotidien : chiffres, liste et textes à publier (page interne publications.html)."""
    auj = datetime.now(PARIS).date()
    jour = jour or auj
    d = await aujourdhui(jour)
    return composer(jour, d["trains"], d["mis_a_jour"], auj)


async def _details(cx, circs) -> list[dict]:
    """Trains complets : gares, retard à chacune, droit d'un voyageur qui y descend."""
    p_ = base.passages.c
    sortie = []
    for c in circs:
        ps = (await cx.execute(select(base.passages).where(p_.circulation_id == c.id).order_by(p_.ordre))).all()
        noms = await _gares(cx, {p.gare for p in ps})
        gares = [{"uic": p.gare, "nom": noms.get(p.gare, p.gare), "arrivee": heure(p.arrivee_prevue),
                  "retard_min": None if p.retard_s is None else p.retard_s // 60, "saute": p.saute,
                  "droit": None if p.ordre == 0 and p.retard_s is None else droit_json(droit_a(c, p.retard_s))}
                 for p in ps]
        sortie.append({"numero": c.numero, "produit": c.produit, "nom": nom_train(c.produit, c.marque),
                       "jour": c.jour.isoformat(), "depart": heure(c.depart_prevu), "supprime": c.supprimee,
                       "cause": c.cause, "region": c.region,
                       "droit_suppression": droit_json(droit_a(c, None)) if c.supprimee else None,
                       "derniere_annonce": heure(c.derniere_annonce), "gares": gares})
    return sortie


@app.get("/api/train")
async def train(numero: str = Query(pattern=r"^\d{1,6}$"), jour: date | None = None):
    """Un train un jour donné (plusieurs circulations possibles sous un même numéro)."""
    jour = jour or datetime.now(PARIS).date()
    c_ = base.circulations.c
    async with app.state.engine.connect() as cx:
        circs = (await cx.execute(select(base.circulations).where(c_.jour == jour, c_.numero == numero))).all()
        if not circs:
            raise HTTPException(404, "Train introuvable ce jour-là")
        return {"trains": await _details(cx, circs)}


def _motif(texte: str) -> str:
    """Motif ILIKE « contient », sans laisser passer les jokers % et _ du visiteur."""
    return "%" + texte.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"


@app.get("/api/recherche")
async def recherche(arrivee: str = Query("", max_length=60), depart: str = Query("", max_length=60)):
    """Sans numéro : trains d'aujourd'hui et d'hier en retard (≥ 1 min) ou supprimés, par gares."""
    arrivee, depart = arrivee.strip(), depart.strip()
    if len(arrivee) < 2 and len(depart) < 2:
        return {"trains": []}
    auj = datetime.now(PARIS).date()
    jours = [auj, date.fromordinal(auj.toordinal() - 1)]
    c_, p_, g_ = base.circulations.c, base.passages.c, base.gares.c
    q = select(base.circulations).where(c_.jour.in_(jours), c_.produit != "?", c_.numero.is_not(None))
    if len(arrivee) >= 2:
        q = q.where(c_.id.in_(select(p_.circulation_id).join(base.gares, g_.uic == p_.gare)
                              .where(g_.nom.ilike(_motif(arrivee), escape="\\"), p_.ordre > 0)))
    if len(depart) >= 2:
        q = q.where(c_.origine.in_(select(g_.uic).where(g_.nom.ilike(_motif(depart), escape="\\"))))
    q = q.where(c_.supprimee | c_.id.in_(select(p_.circulation_id).where(p_.retard_s >= 60)))
    async with app.state.engine.connect() as cx:
        circs = (await cx.execute(q.order_by(c_.jour.desc(), c_.depart_prevu).limit(20))).all()
        return {"trains": await _details(cx, circs)}


if FRONTEND.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="pages")
