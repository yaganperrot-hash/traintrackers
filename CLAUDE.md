# CLAUDE.md

Règles de travail pour Claude Code sur **traintracker** (nom de dépôt provisoire, pas de marque).

## Vue d'ensemble
Détecter les trains SNCF dont le retard ou la suppression ouvre droit à un remboursement, et le faire
savoir aux voyageurs : un post quotidien (publié à la main sur X et Instagram) et un site qui affiche
directement les trains en retard ou supprimés, avec une fonction de recherche de train. On renvoie
vers le formulaire officiel ; on ne dépose jamais de demande à la place du voyageur.
Détails, décisions et contraintes : `PROJECT.md`. Avancement : `ROADMAP.md`.

## Périmètre
- **Dedans** : TGV INOUI, Intercités, Ouigo, TER, trains internationaux (Eurostar, Lyria…),
  opérateurs concurrents sur le réseau (Trenitalia, Renfe…).
- **Dehors** : RER, métro, Transilien.
- Aucune donnée personnelle collectée. Ajouter des comptes ou des alertes utilisateurs = rouvrir le
  sujet RGPD avant d'écrire du code.

## Stack
Reprise de la stack de rertracker (`../rertracker`), dont on reprend la base de calcul en l'adaptant :

| Composant | Technologie |
|-----------|-------------|
| Backend | Python 3.12 + FastAPI |
| Base de données | PostgreSQL 16 |
| ORM | SQLAlchemy 2.x async |
| Scheduler | APScheduler 3.x |
| Frontend | HTML / CSS / JS vanilla |
| Conteneurisation | Docker + docker-compose |

Hébergement : **local pour l'instant**. Puis OVH : VPS de rertracker ou nouveau VPS, à décider
selon la consommation mesurée. Pas de nom de domaine choisi.

## Budget — règle dure
- Aucune dépense en dehors du VPS, de Claude et du domaine. **Pas d'API payante.**
- L'API X est payante → **publication X et Instagram manuelle** : le système génère texte et image,
  l'utilisateur publie.
- Respecter les quotas et conditions de chaque API. Toute affirmation sur un quota ou un tarif se
  vérifie à la source (doc officielle, en-têtes de réponse), jamais de mémoire.

## Veille
Claude assure la veille sur les politiques d'API (X, Instagram, flux SNCF) et sur les règles de
remboursement (G30, Ouigo, règlement européen, TER par région, opérateurs étrangers). Toute évolution
détectée → proposer la modification avec ses sources ; l'utilisateur valide avant application.

## Exécution des tâches
- Avant toute tâche : proposer un plan découpé et ordonné. Ne rien écrire sans accord explicite.
- Plan validé → exécuter jusqu'au bout. Stopper et prévenir si : (a) une zone critique est touchée,
  (b) le plan validé se révèle faux ou incomplet, (c) il faudrait sortir du périmètre.
- Ne modifier que le code concerné par la tâche.
- Une tâche n'est « finie » que testée, tests au vert.
- N'inventer aucun barème ni aucune règle d'éligibilité : chaque règle encodée cite sa source officielle.

## Zones critiques — confirmation obligatoire avant modification
- **Règles d'éligibilité au remboursement** : une erreur fausse tout ce qui est affiché et publié.
- **Secrets** : `.env`, identifiants d'API — jamais en clair dans le code, jamais commités.
- **Rythme de collecte et quotas** des API.
- **Schéma de base de données** et migrations.

## Conventions de rangement
- `backend/` : FastAPI, scheduler, collecte, calcul, génération des posts.
- `frontend/` : HTML/CSS/JS vanilla, une page par vue.
- `tests/` : pytest (`test_*.py`).
- `poc/` : prototype du flux (jalon 1), jetable une fois ses conclusions reportées dans `PROJECT.md`.
- `.claude/` : état de session (`SESSION.md`, `DEBUG.md`, `archive/`, `commands/`).
- `memory/lessons.md` : leçons en attente de promotion en règle ici.
- `TODO.md` à la racine. Rien d'autre de nouveau à la racine sans raison.
- Fichiers texte : `encoding="utf-8"` explicite (projet sous Windows, cp1252 par défaut).
- `zoneinfo` sous Windows : la dépendance `tzdata` est obligatoire (pas de base de fuseaux système).
- Processus longs (collecte de plusieurs jours) : lancer détaché (`Start-Process … -WindowStyle Hidden`,
  PID dans un fichier), jamais via `run_in_background`, tué avec la session Claude.
- Environnement Python : `venv/` à la racine, `venv/Scripts/python`.

## Autorisations
- Création et édition de fichiers dans le projet, commandes de test et de build : OK une fois le plan validé.
- Commit par unité logique ; push si un remote existe.
- **Toujours demander d'abord** : force-push, `git reset --hard`, réécriture d'historique,
  suppression de fichiers ou de branches distantes.
- Ne pas sortir du dossier projet sans accord (lecture de `../rertracker` autorisée pour reprendre du code).

## Rituel de session
Deux commandes locales au projet (`.claude/commands/`) :
- **`/start`** (début de session) : lit `SESSION.md`, `TODO.md`, `DEBUG.md`, `ROADMAP.md`, restitue
  l'état en 3 lignes, situe la session dans les jalons (« jalon courant X/N »), propose un plan et
  attend la validation.
- **`/wrap`** (fin de session) : archive et réécrit `SESSION.md`, met à jour `DEBUG.md`, coche
  `ROADMAP.md`, trie `memory/lessons.md` (leçons durables → règles ici), met à jour l'arbre du
  `README.md`, commit, puis push si un remote existe.
