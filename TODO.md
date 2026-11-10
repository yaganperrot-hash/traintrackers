# TODO

## Décisions en attente (règles — zone critique, accord requis avant modification)
- [ ] **Train de type inconnu supprimé** : `evaluer()` renvoie « remboursement intégral » avant de vérifier
      le produit (ex. le 2026-11-10 : un Transilien Paris Est → Longueville classé « ? »). Proposition : aucun
      droit affirmé pour un type inconnu, même supprimé. Contourné pour l'instant dans `backend/api.py`.
- [ ] **Tutoiement** : les messages de `backend/regles.py` disent « vous » ; le ton du site est le « tu »
      (décidé le 2026-11-08). Proposition : passer ces textes au « tu ».
- [ ] **TGV INOUI international** (ex. 9864 Montpellier → Bruxelles) : traité en G30 national. Au-delà de 3 h,
      le site afficherait 75 % au lieu du plafond international de 50 %. Proposition : reconnaître un train
      international à sa gare de départ ou d'arrivée hors de France.

## Vérifications à faire à la main (sites qui bloquent la lecture automatique)
- [ ] TER Normandie (Krono+), Centre-Val de Loire (Rémi / Rémi Express), Pays de la Loire (suppressions),
      Sud (occasionnels) ; G30 : délai de 90 j et train supprimé. Liens dans `docs/regles-remboursement.md`.

## Prochaine session
- [ ] Jalon 1 : analyse de la journée complète du 2026-11-10 sur le VPS, conclusions dans `PROJECT.md`.
- [ ] Jalon 3 : mesurer la place prise par jour en base (≈ 30 Mo/jour au premier relevé, plus que prévu).
- [ ] Alertes : ignorer l'horodatage pour ne stocker que les vrais changements.
