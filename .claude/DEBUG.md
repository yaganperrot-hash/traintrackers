# Debug — bugs

## En cours
- **Transilien présent dans le flux** (2026-11-07) : ~100 circulations ajoutées `OCESN1xxxxxF`
  (Paris Est–Château-Thierry, Saint-Lazare–Mantes…). Hors périmètre → à filtrer à la collecte (jalon 3).
- **Classification des circulations ajoutées par numéro** : hypothèse (R = car, 1xxxxx = Transilien,
  8xxxxx = TER, 4 chiffres = Intercités), constatée sur un relevé, non documentée. À valider sur
  plusieurs jours avant d'en dépendre.

## Résolus
- 2026-11-07 — **Retard de 6 h d'un Intercités de nuit** (n° 3754, Paris Austerlitz) : **réel**. Panne
  de locomotive à La Souterraine, confirmée par le flux Service Alerts (cause en texte français). L'arrêt
  en `StopArea:` est un arrêt imprévu ajouté. Pas un artefact.
- 2026-11-07 — **Trains « ? » sans produit** : circulations ajoutées hors GTFS, `trip_id` court
  `OCESN<n°><F|R>`. R = cars (surtout cars TER), F = trains, dont une majorité de Transilien.
  Classées dans `poc/analyse.py` (suffixe `*` = produit déduit).
- 2026-11-07 — `ZoneInfoNotFoundError: Europe/Paris` sous Windows : ajout de `tzdata` aux dépendances.
- 2026-11-07 — `poc/analyse.py` : colonne de tableau non séparée et cars TER (`CTE`) classés « ? ».
