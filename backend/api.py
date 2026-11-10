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
from backend.regles import Droit, Statut, evaluer

PARIS = ZoneInfo("Europe/Paris")
FRONTEND = Path(__file__).resolve().parents[1] / "frontend"
CACHE_S = 60

NOMS = {"OUI": "TGV INOUI", "OGO": "OUIGO", "IC": "Intercités", "IC*": "Intercités", "ICN": "Intercités de nuit",
        "LYR": "Lyria", "ICE": "ICE", "TER": "TER", "TER*": "TER", "TT": "Tram-train", "NAV": "Navette",
        "TRN": "Trenitalia"}
NOMS_MARQUE = {"NOMAD_RESA": "TER Krono+", "REMI_EXPRESS": "Rémi Express", "REMI": "Rémi"}
RANG = {Statut.REMBOURSEMENT: 3, Statut.AUTOMATIQUE: 2, Statut.DROIT: 1}


def nom_train(produit: str, marque: str | None) -> str:
    return NOMS_MARQUE.get(marque or "") or NOMS.get(produit, produit)


def heure(dt: datetime | None) -> str | None:
    return dt.astimezone(PARIS).strftime("%H:%M") if dt else None


def droit_json(d: Droit) -> dict:
    return {"statut": d.statut.value, "regle": d.regle, "message": d.message, "pourcentage": d.pourcentage,
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


@app.get("/api/train")
async def train(numero: str = Query(pattern=r"^\d{1,6}$"), jour: date | None = None):
    """Un train un jour donné : ses gares, le retard à chacune et le droit d'un voyageur qui y descend."""
    jour = jour or datetime.now(PARIS).date()
    c_, p_ = base.circulations.c, base.passages.c
    async with app.state.engine.connect() as cx:
        circs = (await cx.execute(select(base.circulations).where(c_.jour == jour, c_.numero == numero))).all()
        if not circs:
            raise HTTPException(404, "Train introuvable ce jour-là")
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
    return {"trains": sortie}


if FRONTEND.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="pages")
