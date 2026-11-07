# PROJECT — traintracker

> Nom de dépôt provisoire. Le projet n'a pas encore de nom de marque.

## Quoi / pourquoi
Suivre le réseau SNCF, calculer retards et suppressions, et identifier les trains qui ouvrent droit
à un remboursement, pour que les voyageurs le sachent et fassent leur demande.

Deux livrables :
1. **Post quotidien** listant les trains ouvrant droit à remboursement, avec le lien pour faire la
   demande. Publié **à la main** sur X et Instagram, sur de nouveaux comptes dédiés.
2. **Site** qui affiche directement les trains en retard ou supprimés, avec une fonction de recherche
   pour trouver son train et obtenir ce qu'il faut pour se faire rembourser.

## Périmètre
- **Dedans** : TGV INOUI, Intercités, Ouigo, TER, trains internationaux (Eurostar, Lyria…),
  opérateurs concurrents sur le réseau (Trenitalia, Renfe…).
- **Hors périmètre** :
  - RER, métro, Transilien.
  - Déposer une demande de remboursement à la place du voyageur : on renvoie vers le formulaire officiel.
  - Toute collecte de données personnelles.

## Pour qui
Les voyageurs grand public.

## Définition de « fini »
Le post quotidien et le site fonctionnent.

## Contraintes
- **Budget** : rien en dehors du VPS, de Claude et du domaine. Pas d'API payante ; quotas et
  conditions des API respectés.
- **Temps** : pas d'échéance, projet mené sur le temps libre.

## Risque principal
**Fiabilité du flux temps réel SNCF** : retard réel à l'arrivée, suppressions, couverture des
opérateurs concurrents et des trains internationaux. → Prototype du flux en premier (jalon 1).

## Décisions (ADR-lite)
- **2026-11-07 — Stack** : celle de rertracker (Python 3.12, FastAPI, PostgreSQL 16, SQLAlchemy async,
  APScheduler, front vanilla, Docker). On reprend sa base de calcul en l'adaptant.
- **2026-11-07 — Hébergement** : local pour l'instant, puis OVH. VPS de rertracker ou nouveau VPS
  selon la consommation mesurée.
- **2026-11-07 — Historique long** : conservé pour alimenter des statistiques sur le site et dans les
  posts. Niveau de détail stocké (brut ou agrégé) à décider après les mesures du prototype.
- **2026-11-07 — Publication manuelle** : l'API X est payante (aucune offre gratuite pour un nouveau
  compte), ce qui sort du budget. Le système génère texte et image, remis par e-mail et sur une page
  `/publications` (mécanisme de rertracker) ; l'utilisateur publie.
- **2026-11-07 — Suivi** : e-mail d'alerte et page d'état si la collecte tombe ou si le post du jour
  n'est pas généré.
- **2026-11-07 — Pas de RGPD** : aucune donnée personnelle. À rouvrir si des comptes ou alertes
  utilisateurs sont ajoutés.
- **2026-11-07 — Veille** : Claude surveille les politiques d'API et les règles de remboursement,
  propose les modifications avec leurs sources ; l'utilisateur valide.

- **2026-11-07 — Tous les trains restent visibles, avec leur explication** : TER et OUIGO sont
  affichés comme les autres. Chaque train porte sa règle : OUIGO = « indemnisation automatique par
  e-mail, rien à faire » ; TER = « pas de remboursement par train pour un voyageur occasionnel » (+ lien
  vers la garantie de la région). Un visiteur qui ne trouve pas son train ne doit jamais croire à un bug.
- **2026-11-07 — Seuil évalué à chaque arrêt** : un train entre dans le post s'il dépasse son seuil à
  au moins un arrêt, avec la mention « selon votre gare d'arrivée ». Le site demande la gare d'arrivée.

## Veille initiale (2026-11-07) — à confirmer aux sources officielles
- **G30** (TGV INOUI, Intercités) : indemnité à partir de 30 min de retard à l'arrivée. Les barèmes
  diffèrent selon les sources → à vérifier dans les conditions officielles avant encodage.
- G30 ne couvre ni TER ni Transilien. TER : règles propres à chaque région.
- **Flux temps réel** : GTFS-RT « Réseau SNCF TGV, Intercités et TER » sur transport.data.gouv.fr,
  sans authentification. Un rapport de validation (mai 2026) signale des erreurs sur des `stop_id`.
  Rafraîchi toutes les 2 min, couvre les trains des 60 prochaines minutes → collecte continue
  obligatoire. Périmètre garanti par la SNCF : TGV et Intercités seulement. Licence ODbL.
  SIRI Lite Estimated Timetable écarté : ~15,6 Mo compressés par appel (≈ 11 Go/jour à 2 min).
- **X** : API en paiement à l'usage, sans offre gratuite (sources tierces, à vérifier sur docs.x.com).
- **Instagram** : publication par API gratuite mais nécessite un compte professionnel et une
  validation Meta. Non retenue pour l'instant (publication manuelle).

## Questions ouvertes
- Nom du projet et nom de domaine.
- Couverture du flux pour Ouigo, les opérateurs concurrents et les trains internationaux.
- Volume de stockage par jour → choix du VPS.
