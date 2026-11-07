# Debug — bugs

## En cours
- **Retards aberrants possibles dans le GTFS-RT** (vu le 2026-11-07) : un Intercités de nuit
  annonçait 120 puis 360 min sur ses deux derniers arrêts, dont un en `StopArea:` au lieu de
  `StopPoint:`. Artefact ou vrai retard ? `poc/analyse.py` liste les retards ≥ 3 h pour vérifier.
- **122 trains « ajoutés » sans produit** (`trip_id` court type `OCESN79026R`, absent du GTFS) :
  à identifier avant de les classer ou de les écarter.

## Résolus
- 2026-11-07 — `ZoneInfoNotFoundError: Europe/Paris` sous Windows : ajout de `tzdata` aux dépendances.
- 2026-11-07 — `poc/analyse.py` : colonne de tableau non séparée et cars TER (`CTE`) classés « ? ».
