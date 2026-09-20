# Bibliothèque de modules — cadrage projet

> Utilisée par `/kickoff` (étape 4). Chaque module ne s'ouvre que si son DÉCLENCHEUR est rempli.
> Les 5 invariants sont TOUJOURS abordés (ils sont dans kickoff.md, pas ici).
> Ajouter un module = ajouter une ligne ici, sans toucher à la commande.

| Module | Déclencheur (axes) | Ce qu'il sonde |
|--------|--------------------|----------------|
| Techno / stack | toujours (profondeur variable) | langages, frameworks, base, choix structurants |
| Cible & déploiement | tourne ailleurs que ma machine | où/comment ça tourne en prod, build, distribution |
| Données & modèle | il y a une base ou une source | schéma, source externe, volumétrie, persistance |
| Légal / RGPD | données personnelles-régulées | consentement, rétention, minimisation, conformité |
| Intégrations externes | dépend d'API / systèmes tiers | quotas, auth, pannes tierces, contrats d'API |
| Multi-agent : rôles & droits | plusieurs agents impliqués | qui crée les tâches, qui code, qui exécute, permissions |
| Communication | produit public / monétisé | comment il se fait connaître, canaux, ASO/store |
| Coûts d'exploitation | hébergement, quotas, tokens LLM | ce que ça coûte à faire tourner, plafonds |
| Observabilité / logs | tourne en prod | logs, alertes, comment on détecte une panne |
| Échelle / charge | plus d'une poignée d'utilisateurs | montée en charge, points de rupture |
| Maintenance / ownership | système maintenu (non jetable) | qui maintient, reprise, dette acceptable |
| Sécurité & zones critiques | secrets OU données | secrets, ce à quoi on ne touche pas sans confirmation |

## Note pour Claude
- Un axe « données personnelles » ouvre RGPD même sur un « petit outil interne » — ne le zappe pas.
- Un prototype jetable n'ouvre ni observabilité, ni échelle, ni maintenance : reste minimal.
- En cas de doute sur l'ouverture d'un module, ouvre-le et laisse-moi le refermer à l'étape 4.
