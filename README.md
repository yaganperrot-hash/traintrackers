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
Sur le serveur, l'application tourne sous Docker (`deploy/docker-compose.yml`).

### Site en local (Windows, sans Docker)
```powershell
powershell -ExecutionPolicy Bypass -File deploy\local.ps1         # lance tout, puis http://127.0.0.1:8000
powershell -ExecutionPolicy Bypass -File deploy\local.ps1 -Stop   # arrête tout
```
Le script démarre PostgreSQL, l'ingestion des relevés de `poc/data/` et l'API avec les pages, en
processus détachés. Les données sont celles du collecteur du PC (`poc/collect.py`) : trous quand le PC
est en veille, moins complètes que sur le VPS.

Mise en place, une fois :
- PostgreSQL 16 dans `%LOCALAPPDATA%\monretard\` (binaires `pg16\`, données `pgdata\`, journaux), hors
  OneDrive. Installé le 2026-11-11 depuis Maven Central (`io.zonky.test.postgres`, 16.15), le
  téléchargement officiel EnterpriseDB étant refusé (403). Écoute sur 127.0.0.1 seulement.
- `.env` à la racine (ignoré par git) : `DATABASE_URL=postgresql://monretard:…@127.0.0.1:5432/monretard`.
- Tests sur vraie base : `DATABASE_URL_TEST` vers la base `monretard_test` (jamais la base `monretard`,
  les tests vident les tables).

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
│   ├── api.py           # API du site + pages (droits calculés à la lecture)
│   ├── publication.py   # post quotidien : chiffres et textes X / Instagram (aucune règle)
│   └── ref/regions.geojson  # contours des régions (france-geojson)
├── tests/               # pytest ; test_base.py tourne sur le VPS (vraie base)
├── docs/
│   ├── regles-remboursement.md  # veille des règles (validé le 2026-11-07)
│   ├── strategie-communication.md  # stratégie de communication (2026-11-11, non mise en œuvre)
│   └── maquettes/       # maquettes « Le reçu », données fictives
│       ├── site.html        # recherche d'un train → verdict
│       ├── aujourdhui.html  # trains qui ouvrent un droit aujourd'hui
│       ├── publications.html # page interne : post du soir (Instagram, X)
│       ├── serveur.py       # serveur local à rechargement auto (127.0.0.1:8000)
│       ├── style.css        # styles partagés
│       └── donnees.js       # trains fictifs + règles simplifiées
├── frontend/            # le vrai site : site.html (Mon train), aujourdhui.html, sur l'API
│   └── publications.html # page interne : post du soir, images PNG 1080 × 1350 et textes à copier
├── deploy/              # Docker du serveur : collecte, Postgres, ingestion (VPS ~/monretard/)
│   └── local.ps1        # site en local sur le PC (PostgreSQL + ingestion + API), sans Docker
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
