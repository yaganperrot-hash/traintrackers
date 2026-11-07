# traintracker

> Nom de dépôt provisoire.

Repère les trains SNCF (TGV INOUI, Intercités, Ouigo, TER, internationaux, opérateurs concurrents)
dont le retard ou la suppression ouvre droit à un remboursement, et le fait savoir aux voyageurs :

- un **post quotidien** à publier sur X et Instagram, avec le lien pour faire la demande ;
- un **site** qui affiche les trains en retard ou supprimés, avec une recherche par train.

Le projet renvoie vers les formulaires officiels ; il ne dépose aucune demande et ne collecte
aucune donnée personnelle.

## Statut
Cadrage terminé. Prochaine étape : prototype du flux temps réel (voir `ROADMAP.md`).

## Stack
Python 3.12 · FastAPI · PostgreSQL 16 · SQLAlchemy 2.x async · APScheduler · HTML/CSS/JS vanilla · Docker

## Installation
À venir avec le premier code (jalon 1). Prévu : `cp .env.example .env`, puis `docker-compose up -d`.

## Structure
```
/
├── .claude/
│   ├── commands/        # /start, /wrap (+ /kickoff)
│   ├── kickoff/         # référentiel des modules de cadrage
│   ├── archive/         # sessions archivées
│   ├── SESSION.md       # état de la session courante
│   └── DEBUG.md         # bugs en cours / résolus
├── memory/
│   └── lessons.md       # leçons en attente de promotion dans CLAUDE.md
├── CLAUDE.md            # règles de travail pour Claude Code
├── PROJECT.md           # quoi/pourquoi, décisions, contraintes, risque
├── ROADMAP.md           # jalons
├── TODO.md
└── README.md
```
