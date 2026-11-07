# ROADMAP — traintracker

> Référentiel d'avancement. `/start` s'y situe, `/wrap` coche les jalons franchis.
> Hypothèse révisable : on amende si un jalon se révèle mal découpé.

- [ ] **1. Prototype du flux** : collecter le GTFS-RT SNCF pendant quelques jours. Vérifier le retard
      à l'arrivée, les suppressions, la couverture des opérateurs (Ouigo, concurrents, internationaux),
      et mesurer le volume par jour. Conclusions reportées dans `PROJECT.md`.
- [ ] **2. Règles de remboursement** : veille sur les sources officielles (G30, Ouigo, règlement
      européen, TER par région, opérateurs étrangers), puis encodage testé, chaque règle citant sa source.
- [ ] **3. Collecte continue et historique** : à partir de la base rertracker adaptée.
- [ ] **4. Post quotidien généré** : texte et image, remis par e-mail et sur la page `/publications`.
- [ ] **5. Site** : trains en retard ou supprimés affichés directement, puis recherche de train avec
      droits et lien vers le formulaire.
- [ ] **6. Suivi** : e-mail d'alerte et page d'état.
- [ ] **7. Déploiement sur OVH** : choix du VPS selon la consommation mesurée.
- [ ] **8. Statistiques** sur le site et dans les posts.
