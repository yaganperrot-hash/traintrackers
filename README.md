# traintracker

> Nom de dépôt provisoire.

Repère les trains SNCF (TGV INOUI, Intercités, Ouigo, TER, internationaux, opérateurs concurrents)
dont le retard ou la suppression ouvre droit à un remboursement, et le fait savoir aux voyageurs :

- un **post quotidien** à publier sur X et Instagram, avec le lien pour faire la demande ;
- un **site** qui affiche les trains en retard ou supprimés, avec une recherche par train.

Le projet renvoie vers les formulaires officiels ; il ne dépose aucune demande et ne collecte
aucune donnée personnelle.

## Statut
Jalon 1 en cours : prototype du flux temps réel SNCF (collecte en cours, voir `poc/README.md`).

## Stack
Python 3.12 · FastAPI · PostgreSQL 16 · SQLAlchemy 2.x async · APScheduler · HTML/CSS/JS vanilla · Docker

## Installation
Python 3.12 requis. Pour le prototype :
```bash
python -m venv venv
venv/Scripts/python -m pip install -r poc/requirements.txt
```
L'application complète (prévue : `cp .env.example .env`, puis `docker-compose up -d`) arrivera avec le jalon 3.

## Structure
```
/
├── .claude/
│   ├── commands/        # /start, /wrap (+ /kickoff)
│   ├── kickoff/         # référentiel des modules de cadrage
│   ├── archive/         # sessions archivées
│   ├── SESSION.md       # état de la session courante
│   └── DEBUG.md         # bugs en cours / résolus
├── docs/
│   ├── regles-remboursement.md  # veille des règles (brouillon à valider)
│   └── maquettes/site.html      # maquette du site, données fictives
├── poc/                 # prototype du flux (jalon 1)
│   ├── collect.py       # collecte GTFS-RT toutes les 2 min
│   ├── analyse.py       # rapport par jour
│   └── data/            # relevés bruts (gitignored)
├── venv/                # environnement Python (gitignored)
├── memory/
│   └── lessons.md       # leçons en attente de promotion dans CLAUDE.md
├── CLAUDE.md            # règles de travail pour Claude Code
├── PROJECT.md           # quoi/pourquoi, décisions, contraintes, risque
├── ROADMAP.md           # jalons
├── TODO.md
└── README.md
```
