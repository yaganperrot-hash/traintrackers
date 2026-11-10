from datetime import date

from google.transit import gtfs_realtime_pb2 as rt

from backend.flux import lire_alertes, lire_trip_updates, nettoyer, numero, produit, uic
from backend.referentiel import Gare, Ligne, Referentiel

TGV = "OCESN9253F1187_F:OUI:FR:Line::2FFF7F96-0EBC-4AA1-B417-38EBD492057E::87686006:83016451:7:1950:20261211"
TRANSILIEN = "OCESN164586F"


def feed(*trains, ts=1794245591) -> bytes:
    m = rt.FeedMessage()
    m.header.gtfs_realtime_version = "2.0"
    m.header.timestamp = ts
    for trip_id, start_date, arrets, annule in trains:
        e = m.entity.add()
        e.id = trip_id
        tu = e.trip_update
        tu.trip.trip_id = trip_id
        tu.trip.start_date = start_date
        if annule:
            tu.trip.schedule_relationship = rt.TripDescriptor.CANCELED
        for stop_id, arrivee, retard, saute in arrets:
            st = tu.stop_time_update.add()
            st.stop_id = stop_id
            if arrivee is None:  # origine : départ seulement
                st.departure.time = 1_794_224_760 + retard
                st.departure.delay = retard
            else:
                st.arrival.time = arrivee + retard
                st.arrival.delay = retard
            if saute:
                st.schedule_relationship = rt.TripUpdate.StopTimeUpdate.SKIPPED
    return m.SerializeToString()


def test_identifiants():
    assert produit(TGV) == "OUI"
    assert numero(TGV) == "9253"
    assert numero("OCESN848506F") == "848506"
    assert numero("autre") is None
    assert uic("StopPoint:OCETGV INOUI-87686006") == "87686006"
    assert uic("StopArea:OCE87686006") == "87686006"
    assert uic("") is None


def test_lecture_retards_et_horaire_theorique():
    contenu = feed((TGV, "20261109", [
        ("StopPoint:OCETGV INOUI-87686006", None, 0, False),
        ("StopPoint:OCETGV INOUI-87725705", 1_794_230_400, 300, False),
        ("StopPoint:OCETGV INOUI-83016451", 1_794_250_500, 2400, False),
    ], False))
    ts, obs = lire_trip_updates(contenu)
    assert ts == 1794245591
    (o,) = obs
    assert o.jour == date(2026, 11, 9) and o.numero == "9253" and o.produit == "OUI" and not o.supprimee
    assert o.depart_prevu == 1_794_224_760
    assert [p.gare for p in o.passages] == ["87686006", "87725705", "83016451"]
    assert o.passages[0].retard_s is None and o.passages[0].arrivee_prevue is None  # origine
    assert o.passages[1].arrivee_prevue == 1_794_230_400 and o.passages[1].retard_s == 300
    assert o.passages[2].retard_s == 2400


def test_suppression_et_arret_saute():
    contenu = feed((TGV, "20261109", [
        ("StopPoint:OCETGV INOUI-87686006", None, 0, False),
        ("StopPoint:OCETGV INOUI-87725705", 1_794_230_400, 0, True),
    ], True))
    (o,) = lire_trip_updates(contenu)[1]
    assert o.supprimee
    assert o.passages[1].saute


def test_hors_perimetre_ignore():
    contenu = feed((TRANSILIEN, "20261109", [("StopPoint:OCETrain TER-87393009", 1_794_230_400, 600, False)], False))
    assert lire_trip_updates(contenu)[1] == []


def test_date_illisible_ignoree():
    assert lire_trip_updates(feed((TGV, "", [], False)))[1] == []


def alertes(*items) -> bytes:
    m = rt.FeedMessage()
    m.header.gtfs_realtime_version = "2.0"
    for i, (trip_ids, titre, description) in enumerate(items):
        e = m.entity.add()
        e.id = str(i)
        for t in trip_ids:
            e.alert.informed_entity.add().trip.trip_id = t
        e.alert.header_text.translation.add(text=titre, language="fr")
        e.alert.header_text.translation.add(text="Delay", language="en")
        e.alert.description_text.translation.add(text=description, language="fr")
    return m.SerializeToString()


def test_causes_titre_ou_description():
    causes = lire_alertes(alertes(
        (["OCESN9253F"], "Panne de signalisation.", "<p>détails</p>"),
        (["OCESN861359F"], "Plus d'informations :", "<p><span>\xa0</span>Panne d'une installation&nbsp;: retards</p>"),
        (["OCESN111111F"], "Plus d'information :", ""),
    ))
    assert causes["9253"] == "Panne de signalisation"
    assert causes["861359"] == "Panne d'une installation : retards"
    assert "111111" not in causes


def test_nettoyer_coupe_et_retire_le_html():
    assert nettoyer("<b>A</b>&amp;  B") == "A & B"
    assert len(nettoyer("x" * 500)) == 300


def test_region_et_marque_par_ligne():
    ref = Referentiel(
        gares={"87411017": Gare("87411017", "Le Havre", "Normandie", 0, 0),
               "87384008": Gare("87384008", "Paris Saint-Lazare", "Île-de-France", 0, 0)},
        lignes={"t1": Ligne("K1+", "Paris - Le Havre")})
    assert ref.region_et_marque("TER", "t1", ["87384008", "87411017"]) == ("Normandie", "NOMAD_RESA", False)
    assert ref.region_et_marque("OUI", "t1", ["87384008"]) == (None, None, False)
    # Ligne inconnue : région majoritaire hors Île-de-France, sans marque
    assert ref.region_et_marque("TER", "t2", ["87384008", "87411017"]) == ("Normandie", None, False)
    assert ref.region_et_marque("TER", "t2", []) == (None, None, False)
