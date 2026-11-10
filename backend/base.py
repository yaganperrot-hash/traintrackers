"""Base de données — ZONE CRITIQUE (schéma validé par l'utilisateur le 2026-11-10).

On stocke des faits, jamais des verdicts : les droits sont recalculés à l'affichage par
backend/regles.py, pour qu'une correction de règle s'applique à tout l'historique.

Tables :
  circulations : un train un jour donné
  passages     : un train à une gare (dernier retard annoncé)
  gares        : nom, région, position (GTFS théorique)
  collectes    : un relevé traité (journal, page d'état)
Conservation : illimitée (≈ 2 Go/an estimés). Aucune donnée personnelle.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

from sqlalchemy import (BigInteger, Boolean, Column, Date, DateTime, Float, ForeignKey, Index, Integer,
                        MetaData, SmallInteger, String, Table, Text, UniqueConstraint, bindparam,
                        select, update)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

meta = MetaData()

gares = Table(
    "gares", meta,
    Column("uic", String(8), primary_key=True),
    Column("nom", Text, nullable=False),
    Column("region", Text),
    Column("lat", Float),
    Column("lon", Float),
)

circulations = Table(
    "circulations", meta,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("jour", Date, nullable=False),              # jour de départ (start_date du flux)
    Column("trip_id", Text, nullable=False),
    Column("numero", String(8)),
    Column("produit", String(16), nullable=False),     # OUI, OGO, IC, TER…
    Column("ligne_code", Text),
    Column("ligne_nom", Text),
    Column("region", Text),                            # TER seulement
    Column("marque", String(16)),                      # NOMAD_RESA, REMI_EXPRESS, REMI
    Column("marque_a_confirmer", Boolean, nullable=False, default=False),
    Column("origine", String(8)),                      # UIC
    Column("terminus", String(8)),                     # UIC
    Column("depart_prevu", DateTime(timezone=True)),
    Column("supprimee", Boolean, nullable=False, default=False),
    Column("cause", Text),                             # dernière cause annoncée (Service Alerts)
    Column("premiere_annonce", DateTime(timezone=True), nullable=False),
    Column("derniere_annonce", DateTime(timezone=True), nullable=False),
    UniqueConstraint("jour", "trip_id", name="uq_circulation"),
    Index("ix_circulations_jour_numero", "jour", "numero"),
)

passages = Table(
    "passages", meta,
    Column("circulation_id", BigInteger, ForeignKey("circulations.id", ondelete="CASCADE"), primary_key=True),
    Column("gare", String(8), primary_key=True),       # UIC
    Column("ordre", SmallInteger, nullable=False),
    Column("arrivee_prevue", DateTime(timezone=True)),
    Column("retard_s", Integer),                       # dernier retard à l'arrivée annoncé
    Column("saute", Boolean, nullable=False, default=False),
    Column("annonce_le", DateTime(timezone=True), nullable=False),  # relevé de cette dernière valeur
)

collectes = Table(
    "collectes", meta,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("fichier", Text, nullable=False, unique=True),  # trip_updates/AAAA-MM-JJ/HHMMSS.pb.gz
    Column("releve_le", DateTime(timezone=True)),          # horodatage du flux
    Column("traite_le", DateTime(timezone=True), nullable=False),
    Column("trains", Integer),
    Column("erreur", Text),
)


def url_base() -> str:
    url = os.environ["DATABASE_URL"]  # jamais en clair dans le code : fichier .env du serveur
    return url.replace("postgresql://", "postgresql+asyncpg://", 1)


def moteur(url: str | None = None) -> AsyncEngine:
    return create_async_engine(url or url_base(), pool_size=2, max_overflow=0)


async def creer_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as cx:
        await cx.run_sync(meta.create_all)


def horodatage(epoch: int | None) -> datetime | None:
    return datetime.fromtimestamp(epoch, timezone.utc) if epoch else None


async def ecrire_gares(cx: AsyncConnection, lignes: list[dict]) -> None:
    for i in range(0, len(lignes), 1000):
        q = insert(gares).values(lignes[i:i + 1000])
        await cx.execute(q.on_conflict_do_update(
            index_elements=[gares.c.uic],
            set_={"nom": q.excluded.nom, "region": q.excluded.region, "lat": q.excluded.lat, "lon": q.excluded.lon}))


async def ecrire_circulations(cx: AsyncConnection, lignes: list[dict]) -> dict[tuple, int]:
    """Insère ou met à jour ; renvoie (jour, trip_id) → id. Une annonce plus ancienne n'écrase rien."""
    ids: dict[tuple, int] = {}
    for i in range(0, len(lignes), 500):
        q = insert(circulations).values(lignes[i:i + 500])
        maj = {c: getattr(q.excluded, c) for c in (
            "numero", "produit", "ligne_code", "ligne_nom", "region", "marque", "marque_a_confirmer",
            "origine", "terminus", "depart_prevu", "supprimee", "derniere_annonce")}
        # La cause est écrite à part (ecrire_causes) : une alerte qui disparaît n'efface rien.
        q = q.on_conflict_do_update(
            constraint="uq_circulation", set_=maj,
            where=circulations.c.derniere_annonce <= q.excluded.derniere_annonce,
        ).returning(circulations.c.id, circulations.c.jour, circulations.c.trip_id)
        for r in (await cx.execute(q)).all():
            ids[(r.jour, r.trip_id)] = r.id
    manquants = [(l["jour"], l["trip_id"]) for l in lignes if (l["jour"], l["trip_id"]) not in ids]
    if manquants:  # lignes non modifiées (annonce plus ancienne) : on récupère quand même leur id
        for jour in {j for j, _ in manquants}:
            tids = [t for j, t in manquants if j == jour]
            res = await cx.execute(select(circulations.c.id, circulations.c.trip_id)
                                   .where(circulations.c.jour == jour, circulations.c.trip_id.in_(tids)))
            for r in res.all():
                ids[(jour, r.trip_id)] = r.id
    return ids


async def ecrire_causes(cx: AsyncConnection, jour_causes: list[dict]) -> None:
    """jour_causes : [{"id": circulation_id, "cause": texte}]"""
    if jour_causes:
        await cx.execute(update(circulations).where(circulations.c.id == bindparam("cid"))
                         .values(cause=bindparam("nouvelle_cause")),
                         [{"cid": d["id"], "nouvelle_cause": d["cause"]} for d in jour_causes])


async def ecrire_passages(cx: AsyncConnection, lignes: list[dict]) -> None:
    for i in range(0, len(lignes), 1000):
        q = insert(passages).values(lignes[i:i + 1000])
        await cx.execute(q.on_conflict_do_update(
            index_elements=[passages.c.circulation_id, passages.c.gare],
            set_={"ordre": q.excluded.ordre, "arrivee_prevue": q.excluded.arrivee_prevue,
                  "retard_s": q.excluded.retard_s, "saute": q.excluded.saute, "annonce_le": q.excluded.annonce_le},
            where=passages.c.annonce_le <= q.excluded.annonce_le))


async def deja_traite(cx: AsyncConnection) -> set[str]:
    return set((await cx.execute(select(collectes.c.fichier))).scalars().all())


async def noter_collecte(cx: AsyncConnection, fichier: str, releve_le: datetime | None,
                         trains: int | None, erreur: str | None = None) -> None:
    q = insert(collectes).values(fichier=fichier, releve_le=releve_le, traite_le=datetime.now(timezone.utc),
                                 trains=trains, erreur=erreur)
    await cx.execute(q.on_conflict_do_nothing(index_elements=[collectes.c.fichier]))
