"""Post quotidien : chiffres et textes (backend/publication.py). Sans base."""
from datetime import date

from backend.publication import composer, date_courte, date_longue, duree, longueur_x

JOUR = date(2026, 11, 12)  # un jeudi


def train(numero, retard=None, supprime=False, nom="TGV INOUI", origine="Paris Gare de Lyon",
          terminus="Marseille Saint-Charles", statut=None):
    return {"numero": numero, "nom": nom, "origine": origine, "terminus": terminus,
            "supprime": supprime, "retard_max_min": retard,
            "droit": {"statut": statut or ("remboursement" if supprime else "droit")}}


def test_dates_et_durees():
    assert date_longue(JOUR) == "Jeudi 12 novembre"
    assert date_courte(JOUR) == "Jeu. 12 novembre"
    assert date_longue(date(2026, 8, 1)) == "Samedi 1 août"
    assert duree(47) == "+47 min" and duree(60) == "+1 h 00" and duree(134) == "+2 h 14"


def test_longueur_x_compte_une_adresse_pour_23():
    assert longueur_x("monretard.fr") == 23
    assert longueur_x("Voir → monretard.fr/aujourdhui") == len("Voir → ") + 23


def test_aucun_train():
    p = composer(JOUR, [], "21:00", JOUR)
    assert p["n"] == 0 and p["pire"] is None and p["trains"] == []
    assert p["textes"]["x"].startswith("Aucun train ne t'ouvre de droit aujourd'hui.")
    assert "monretard.fr" in p["textes"]["x"] and "monretard.fr" in p["textes"]["instagram"]
    assert p["arrete_a"] == "21 h"


def test_un_seul_train_au_singulier():
    p = composer(JOUR, [train("6611", 74)], "21:04", JOUR)
    assert p["textes"]["x"].startswith("1 train t'ouvre un droit aujourd'hui.\n")
    assert "Le plus gros retard : TGV INOUI 6611, +1 h 14." in p["textes"]["x"]
    assert p["arrete_a"] == "21 h 04"


def test_plusieurs_trains_supprimes_en_tete_puis_retard_decroissant():
    p = composer(JOUR, [train("6611", 74), train("4756", None, supprime=True, nom="Intercités"),
                        train("7801", 190, nom="OUIGO"), train("5102", 35)], "21:30", JOUR)
    assert [t["num"] for t in p["trains"]] == ["4756", "7801", "6611", "5102"]
    assert p["n"] == 4 and p["n_supprimes"] == 1
    assert p["pire"]["num"] == "7801"  # le pire retard n'est jamais un train supprimé
    assert p["textes"]["x"].startswith("4 trains t'ouvrent un droit aujourd'hui, dont 1 supprimé.\n")
    ig = p["textes"]["instagram"]
    assert ig.startswith("Jeudi 12 novembre : 4 trains t'ouvrent un droit.")
    assert "OUIGO 7801 Paris Gare de Lyon → Marseille Saint-Charles, +3 h 10." in ig
    assert "1 train supprimé : remboursement intégral." in ig
    assert "retard à ta gare d'arrivée" in ig
    assert p["trains"][0] == {"prod": "Intercités", "num": "4756", "sup": True, "r": 0,
                              "route": "Paris Gare de Lyon → Marseille Saint-Charles"}


def test_que_des_suppressions_pas_de_pire_retard():
    p = composer(JOUR, [train("1", supprime=True), train("2", supprime=True)], "21:00", JOUR)
    assert p["pire"] is None and "plus gros retard" not in p["textes"]["x"]
    assert "dont 2 supprimés" in p["textes"]["x"]


def test_remboursement_integral_seulement_si_c_est_le_droit_calcule():
    # Un TER supprimé peut n'ouvrir qu'un bon d'achat : on ne promet pas un remboursement intégral.
    ter = train("857312", supprime=True, nom="TER", statut="droit")
    mixte = composer(JOUR, [train("4756", supprime=True), ter], "21:00", JOUR)["textes"]["instagram"]
    assert "2 trains supprimés, dont 1 avec remboursement intégral." in mixte
    aucun = composer(JOUR, [ter], "21:00", JOUR)["textes"]["instagram"]
    assert "1 train supprimé.\n" in aucun and "remboursement intégral" not in aucun


def test_jour_passe():
    hier = composer(date(2026, 11, 11), [train("6611", 74)], "21:00", JOUR)
    assert "un droit hier." in hier["textes"]["x"] and hier["arrete_a"] is None
    avant = composer(date(2026, 11, 9), [], "21:00", JOUR)
    assert "de droit le lundi 9 novembre." in avant["textes"]["x"]


def test_textes_dans_les_limites_meme_un_jour_de_greve():
    trains = [train(str(5000 + i), 30 + i, supprime=i % 4 == 0, nom="Intercités de nuit",
                    origine="Saint-Pierre-des-Corps", terminus="Marseille Saint-Charles") for i in range(900)]
    p = composer(JOUR, trains, "21:59", JOUR)
    assert p["longueurs"]["x"] <= p["longueurs"]["x_max"] == 280
    assert p["longueurs"]["instagram"] <= p["longueurs"]["instagram_max"] == 2200
    assert p["longueurs"]["x"] == longueur_x(p["textes"]["x"])


def test_numero_absent():
    p = composer(JOUR, [train(None, 45)], None, JOUR)
    assert p["trains"][0]["num"] == "" and p["arrete_a"] is None
