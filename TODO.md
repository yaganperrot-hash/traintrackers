# TODO

## Décisions en attente (règles — zone critique, accord requis avant modification)
> Les deux décisions non cochées sont mises de côté (choix du 2026-11-12), pas abandonnées.
- [ ] **Train de type inconnu supprimé** : `evaluer()` renvoie « remboursement intégral » avant de vérifier
      le produit (ex. le 2026-11-10 : un Transilien Paris Est → Longueville classé « ? »). Proposition : aucun
      droit affirmé pour un type inconnu, même supprimé. Contourné pour l'instant dans `backend/api.py`.
- [x] **Tutoiement** : messages de `backend/regles.py` passés au « tu » le 2026-11-12 (textes seuls, aucune
      règle modifiée). À déployer sur le VPS.
- [ ] **TGV INOUI international** (ex. 9864 Montpellier → Bruxelles) : traité en G30 national. Au-delà de 3 h,
      le site afficherait 75 % au lieu du plafond international de 50 %. Proposition : reconnaître un train
      international à sa gare de départ ou d'arrivée hors de France.

## Vérifications à faire à la main (sites qui bloquent la lecture automatique)
- [ ] TER Normandie (Krono+), Centre-Val de Loire (Rémi / Rémi Express), Pays de la Loire (suppressions),
      Sud (occasionnels) ; G30 : délai de 90 j et train supprimé. Liens dans `docs/regles-remboursement.md`.

## Post quotidien (jalon 4) — reste à faire
- [ ] **Envoi par e-mail** du post du soir : demande un compte d'envoi et un secret dans `.env` (zone critique).
- [ ] **Déclenchement à heure fixe** (scheduler) : sans e-mail il n'y a rien à déclencher, la page
      `/publications.html` calcule le post à la demande (« arrêté à » = heure du dernier relevé). À faire avec l'e-mail.
- [ ] **Heure du post** : 21 h proposé, les trains du soir n'y sont pas. À trancher.
- [ ] `publications.html` est servie comme les autres pages (`noindex` seulement) : la protéger ou la sortir
      du site avant la mise en ligne publique.
- [ ] Déployer sur le VPS (connexion SSH refusée à Claude le 2026-11-14 : à lancer à la main).

## Prochaine session
- [ ] Jalon 1 : analyse de la journée complète du 2026-11-10 sur le VPS, conclusions dans `PROJECT.md`.
- [ ] Jalon 3 : mesurer la place prise par jour en base (≈ 30 Mo/jour au premier relevé, plus que prévu).
- [ ] Alertes : ignorer l'horodatage pour ne stocker que les vrais changements.
