# Session — état courant

_Mis à jour le 2026-11-07._

## Objectif courant
Jalon 1/8 — prototype du flux : savoir si le GTFS-RT SNCF permet de détecter de façon fiable les
trains ouvrant droit à remboursement.

## Où on en est
- Cadrage terminé (`CLAUDE.md`, `PROJECT.md`, `ROADMAP.md`, `README.md`).
- Python 3.12 installé (compte utilisateur) + `venv/` à la racine.
- `poc/collect.py` tourne **en arrière-plan détaché** depuis le 2026-11-07 10:45 (PID dans
  `poc/data/collect.pid`) : Trip Updates + Service Alerts toutes les 2 min, ~200 Mo/jour.
  S'arrête si le PC s'éteint ou se met en veille → relancer (voir `poc/README.md`).
- `poc/analyse.py` écrit et testé sur un relevé.
- Premier relevé : retard en secondes par arrêt, `CANCELED` / `SKIPPED` présents ; produits vus
  OUI, OGO, IC, TER, LYR, ICE, TRN, CTE, TT ; Eurostar et Renfe absents ; 122 trains « ajoutés »
  sans produit identifiable.
- SIRI Estimated Timetable écarté du POC (15,6 Mo compressés par appel ≈ 11 Go/jour).
- Remote : `origin` = git@github.com:yaganperrot-hash/traintrackers.git (poussé le 2026-11-07).

## Prochaine étape
1. Vérifier que le collecteur a tourné sans trou (`poc/data/collect.log`).
2. `venv/Scripts/python poc/analyse.py` sur les journées complètes.
3. Reporter les conclusions dans `PROJECT.md` (fiabilité, couverture, stockage/jour).
