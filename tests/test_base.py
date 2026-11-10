"""Tests sur une vraie base PostgreSQL. Ignorés sans DATABASE_URL_TEST (lancés sur le VPS, voir deploy/)."""
import asyncio
import gzip
import os
from pathlib import Path

import pytest

URL = os.environ.get("DATABASE_URL_TEST")
pytestmark = pytest.mark.skipif(not URL, reason="DATABASE_URL_TEST absent")

from tests.test_flux import TGV, alertes, feed  # noqa: E402

ARRETS = [("StopPoint:OCETGV INOUI-87686006", None, 0, False),
          ("StopPoint:OCETGV INOUI-83016451", 1_794_250_500, 0, False)]


def ecrire(dossier: Path, flux: str, cle: str, contenu: bytes) -> None:
    jour, heure = cle.split("/")
    (dossier / flux / jour).mkdir(parents=True, exist_ok=True)
    f = dossier / flux / jour / f"{heure}.pb.gz"
    f.write_bytes(gzip.compress(contenu))
    os.utime(f, (0, 0))  # assez vieux pour être traité


def avec_retard(retard, ts):
    return feed((TGV, "20261109", [ARRETS[0], (ARRETS[1][0], ARRETS[1][1], retard, False)], False), ts=ts)


async def scenario(tmp_path: Path):
    from sqlalchemy import select, text

    from backend import base
    from backend.ingestion import Ingestion

    engine = base.moteur(URL.replace("postgresql://", "postgresql+asyncpg://", 1))
    async with engine.begin() as cx:
        await cx.run_sync(base.meta.drop_all)
    await base.creer_schema(engine)
    ing = Ingestion(engine, tmp_path)
    ing.regions = None  # pas de GTFS dans ce test : référentiel absent

    ecrire(tmp_path, "trip_updates", "2026-11-09/120000", avec_retard(600, 1_794_240_000))
    ecrire(tmp_path, "service_alerts", "2026-11-09/120000", alertes((["OCESN9253F"], "Panne de signalisation", "")))
    ecrire(tmp_path, "trip_updates", "2026-11-09/120200", avec_retard(2400, 1_794_240_120))
    ecrire(tmp_path, "trip_updates", "2026-11-09/120400", bytes([0x0A, 0xFF]))  # message tronqué
    assert await ing.tour() == 3
    assert await ing.tour() == 0  # déjà traités

    async with engine.connect() as cx:
        (c,) = (await cx.execute(select(base.circulations))).all()
        assert (c.numero, c.produit, c.supprimee, c.cause) == ("9253", "OUI", False, "Panne de signalisation")
        assert c.origine == "87686006" and c.terminus == "83016451"
        ps = {p.gare: p for p in (await cx.execute(select(base.passages))).all()}
        assert ps["83016451"].retard_s == 2400  # le dernier retard annoncé
        assert ps["87686006"].retard_s is None
        erreurs = (await cx.execute(text("select count(*) from collectes where erreur is not null"))).scalar()
        assert erreurs == 1

    # Rejouer un relevé plus ancien (nouvelle instance, cache vide) n'écrase pas le plus récent.
    async with engine.begin() as cx:
        await cx.execute(text("delete from collectes where fichier like '%120000%'"))
    ing2 = Ingestion(engine, tmp_path)
    ing2.regions = None
    await ing2.tour()
    async with engine.connect() as cx:
        p = (await cx.execute(select(base.passages).where(base.passages.c.gare == "83016451"))).one()
        assert p.retard_s == 2400
    await engine.dispose()


def test_ingestion_bout_en_bout(tmp_path):
    asyncio.run(scenario(tmp_path))
