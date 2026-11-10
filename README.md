# traintracker

> Nom de dépôt provisoire.

Repère les trains SNCF (TGV INOUI, Intercités, Ouigo, TER, internationaux, opérateurs concurrents)
dont le retard ou la suppression ouvre droit à un remboursement, et le fait savoir aux voyageurs :

- un **post quotidien** à publier sur X et Instagram, avec le lien pour faire la demande ;
- un **site** qui affiche les trains en retard ou supprimés, avec une recherche par train.

Le projet renvoie vers les formulaires officiels ; il ne dépose aucune demande et ne collecte
aucune donnée personnelle.

## Statut
Jalon 1 en cours : prototype du flux temps réel SNCF (collecte sur le VPS, voir `poc/README.md`).

## Stack
Python 3.12 · FastAPI · PostgreSQL 16 · SQLAlchemy 2.x async · APScheduler · HTML/CSS/JS vanilla · Docker

## Installation
Python 3.12 requis. Pour le prototype :
```bash
python -m venv venv
venv/Scripts/python -m pip install -r poc/requirements.txt
venv/Scripts/python -m pip install -r requirements.txt
venv/Scripts/python -m pytest -q   # tests
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
├── backend/
│   ├── regles.py        # règles d'éligibilité au remboursement (zone critique)
│   ├── marques.py       # marque et région des TER à garantie, par ligne GTFS (zone critique)
│   ├── flux.py          # lecture du flux temps réel (retards, suppressions, causes)
│   ├── referentiel.py   # gares, régions et lignes tirées du GTFS théorique
│   ├── base.py          # schéma et écritures PostgreSQL (zone critique)
│   ├── ingestion.py     # relevés bruts → base, toutes les 30 s
│   └── ref/regions.geojson  # contours des régions (france-geojson)
├── tests/               # pytest ; test_base.py tourne sur le VPS (vraie base)
├── docs/
│   ├── regles-remboursement.md  # veille des règles (validé le 2026-11-07)
│   └── maquettes/       # maquettes « Le reçu », données fictives
│       ├── site.html        # recherche d'un train → verdict
│       ├── aujourdhui.html  # trains qui ouvrent un droit aujourd'hui
│       ├── publications.html # page interne : post du soir (Instagram, X)
│       ├── serveur.py       # serveur local à rechargement auto (127.0.0.1:8000)
│       ├── style.css        # styles partagés
│       └── donnees.js       # trains fictifs + règles simplifiées
├── deploy/              # Docker du serveur : collecte, Postgres, ingestion (VPS ~/monretard/)
├── poc/                 # prototype du flux (jalon 1)
│   ├── collect.py       # collecte GTFS-RT toutes les 2 min
│   ├── analyse.py       # rapport par jour
│   ├── regions.py       # gares et TER → région
│   ├── Dockerfile, docker-compose.yml  # collecte sur le VPS (~/monretard/)
│   └── data/            # relevés bruts (gitignored)
├── venv/                # environnement Python (gitignored)
├── memory/
│   └── lessons.md       # leçons en attente de promotion dans CLAUDE.md
├── .impeccable/         # brief de surface et décisions de design (plugin Impeccable)
├── CLAUDE.md            # règles de travail pour Claude Code
├── PRODUCT.md           # publics, ton, principes du produit
├── DESIGN.md            # système visuel « Le reçu »
├── PROJECT.md           # quoi/pourquoi, décisions, contraintes, risque
├── ROADMAP.md           # jalons
├── requirements.txt     # dépendances (pytest pour l'instant)
├── pytest.ini
├── TODO.md
└── README.md
```
