"""API sur une vraie base. Ignorés sans DATABASE_URL_TEST (lancés sur le VPS)."""
import asyncio
import os
from datetime import date, datetime, timezone

import pytest

URL = os.environ.get("DATABASE_URL_TEST")
pytestmark = pytest.mark.skipif(not URL, reason="DATABASE_URL_TEST absent")

JOUR = date(2026, 11, 9)
T = datetime(2026, 11, 9, 12, 0, tzinfo=timezone.utc)


async def remplir():
    from backend import base
    engine = base.moteur(URL.replace("postgresql://", "postgresql+asyncpg://", 1))
    async with engine.begin() as cx:
        await cx.run_sync(base.meta.drop_all)
        await cx.run_sync(base.meta.create_all)
        await base.ecrire_gares(cx, [{"uic": "87686006", "nom": "Paris Gare de Lyon", "region": "Île-de-France", "lat": 0, "lon": 0},
                                     {"uic": "87751008", "nom": "Marseille Saint-Charles", "region": None, "lat": 0, "lon": 0},
                                     {"uic": "87723197", "nom": "Lyon Part-Dieu", "region": None, "lat": 0, "lon": 0}])
        commun = {"jour": JOUR, "marque_a_confirmer": False, "region": None, "marque": None, "ligne_code": None,
                  "ligne_nom": None, "depart_prevu": T, "premiere_annonce": T, "derniere_annonce": T}
        ids = await base.ecrire_circulations(cx, [
            {**commun, "trip_id": "a", "numero": "6611", "produit": "OUI", "origine": "87686006", "terminus": "87751008", "supprimee": False},
            {**commun, "trip_id": "b", "numero": "6613", "produit": "OUI", "origine": "87686006", "terminus": "87751008", "supprimee": False},
            {**commun, "trip_id": "c", "numero": "4756", "produit": "IC", "origine": "87686006", "terminus": "87751008", "supprimee": True},
        ])
        p = lambda cid, gare, ordre, r: {"circulation_id": cid, "gare": gare, "ordre": ordre, "arrivee_prevue": T,
                                         "retard_s": r, "saute": False, "annonce_le": T}
        await base.ecrire_passages(cx, [
            p(ids[(JOUR, "a")], "87686006", 0, None), p(ids[(JOUR, "a")], "87723197", 1, 20 * 60),
            p(ids[(JOUR, "a")], "87751008", 2, 74 * 60),
            p(ids[(JOUR, "b")], "87686006", 0, None), p(ids[(JOUR, "b")], "87751008", 1, 10 * 60),
        ])
    await engine.dispose()


def test_api(monkeypatch):
    asyncio.run(remplir())
    monkeypatch.setenv("DATABASE_URL", URL)
    from fastapi.testclient import TestClient

    from backend.api import app
    with TestClient(app) as client:
        d = client.get("/api/aujourdhui", params={"jour": "2026-11-09"}).json()
        assert [t["numero"] for t in d["trains"]] == ["4756", "6611"]  # supprimé d'abord ; 6613 (+10) sans droit
        assert d["trains"][1]["retard_max_min"] == 74 and d["trains"][1]["droit"]["pourcentage"] == 25
        assert d["trains"][1]["origine"] == "Paris Gare de Lyon"
        assert d["trains"][0]["droit"]["statut"] == "remboursement"

        t = client.get("/api/train", params={"numero": "6611", "jour": "2026-11-09"}).json()["trains"][0]
        assert [g["nom"] for g in t["gares"]] == ["Paris Gare de Lyon", "Lyon Part-Dieu", "Marseille Saint-Charles"]
        assert t["gares"][0]["droit"] is None                    # gare de départ
        assert t["gares"][1]["droit"]["statut"] == "aucun"        # +20 à Lyon : sous le seuil G30
        assert t["gares"][2]["droit"]["statut"] == "droit"        # +74 à Marseille

        assert client.get("/api/train", params={"numero": "9999", "jour": "2026-11-09"}).status_code == 404
        assert client.get("/api/train", params={"numero": "abc"}).status_code == 422
