---
description: Cadrage d'un nouveau projet — entretien adaptatif, puis génération des fichiers de base.
---
---
description: Cadrage d'un nouveau projet — scaffold, entretien adaptatif, génération des fichiers de base.
---
Tu conduis le cadrage d'un NOUVEAU projet. Objectif : poser la structure, mener un entretien
court et ADAPTÉ, puis générer les fichiers de base. Ce n'est PAS un questionnaire : tu sélectionnes
ce qui est pertinent et tu écartes le reste à voix haute.

Déroulé strict, dans l'ordre :

## 1. Scaffold mécanique (aucune question, sauf le remote en fin d'étape)
a. Si le dossier n'est pas déjà un dépôt git : `git init`.
b. Crée un `.gitignore` de base (au minimum : `.env`, `logs/`, fichiers générés). Tu l'affineras
   après l'entretien selon la stack.
c. Crée les stubs VIDES (en-têtes seulement, AUCUN contenu inventé) :
   `TODO.md` (À LA RACINE), `.claude/SESSION.md`, `.claude/DEBUG.md`, `memory/lessons.md`,
   `.claude/archive/.gitkeep`. Ne pas écraser un fichier existant.
d. Écris les deux commandes de session dans `.claude/commands/start.md` et `.claude/commands/wrap.md`
   avec EXACTEMENT le contenu des blocs « FICHIER start.md » et « FICHIER wrap.md » en fin de document.
e. Demande UNE fois : « URL du dépôt distant ? (laisse vide si pas encore créé) ».
   URL fournie → `git remote add origin <url>`. Vide → ne rien configurer, on branchera plus tard.
f. `git add -A && git commit -m "chore: scaffold initial"`.

## 2. Demander le projet
Une seule question ouverte : « Décris ton projet — quoi, pourquoi, et pour qui ? »
Ne pose rien d'autre à ce stade.

## 3. Classer sur 4 axes (silencieusement, à partir de la réponse)
- Qui consomme : moi seul / équipe interne / public externe / d'autres machines (lib, API)
- Où ça tourne : ma machine / service hébergé / distribué aux utilisateurs / embarqué
- Durée de vie : prototype jetable / système maintenu
- Sensibilité des données : aucune / interne / personnelles-régulées
Si un axe est indéterminable, pose UNE question ciblée pour le lever. Pas plus.

## 4. Sélectionner les modules et l'ANNONCER
Lis `.claude/kickoff/modules.md`. Sélectionne les modules dont le déclencheur est rempli par
les 4 axes. Puis annonce, en une fois :
- les points que tu vas aborder,
- ceux que tu écartes ET POURQUOI (ex. « je passe déploiement, comm et échelle : outil interne
  sur ta machine »).
Termine par : « Corrige si l'un des points écartés compte quand même. » ATTENDS ma réponse.

## 5. Entretien
Aborde les 5 INVARIANTS (toujours) + les modules retenus. Règles dures :
- Une question à la fois. Concis.
- NE JAMAIS reposer une question dont la réponse est déjà déductible de ce qui a été dit.
- N'INVENTE RIEN. Tout ce qui ira dans les fichiers doit avoir été dit ou validé par moi.
  Une inférence non confirmée n'est pas un fait : demande, ou laisse vide.

Les 5 invariants :
1. Quoi / pourquoi / HORS-périmètre (ce qu'on ne fait pas).
2. Pour qui (utilisateurs / parties prenantes, même si « moi seul »).
3. Définition de « fini » / critères de succès.
4. Contraintes dures (temps, budget, légal, dépendances imposées).
5. Le plus gros inconnu / ce qui peut tuer le projet (candidat à un POC précoce).

## 6. Synthèse + validation
Présente une synthèse compacte : périmètre, pour qui, succès, contraintes, risque principal,
stack, décisions, zones critiques, jalons pressentis, points écartés. Puis :
« Je génère les fichiers sur cette base ? » ATTENDS mon OK. Ne génère RIEN avant.

## 7. Génération (après OK seulement)
Génère, à partir de la SEULE synthèse validée :
- `CLAUDE.md` — règles de travail + archi. < 200 lignes. Inclure : exécution des tâches,
  zones critiques, conventions de rangement, autorisations, ET une section « Rituel de session »
  décrivant `/start` (début) et `/wrap` (fin). NE PAS écrire que ces commandes viennent d'un
  plugin — elles sont locales au projet.
- `PROJECT.md` — quoi/pourquoi, pour qui, décisions (ADR-lite datées), contraintes, risque.
- `README.md` — présentation + install + structure.
- `ROADMAP.md` — les jalons issus de l'entretien, en cases à cocher `- [ ]`. C'est le
  référentiel d'avancement : `/start` s'y situe, `/wrap` y coche les jalons franchis.
Affine le `.gitignore` selon la stack, puis commit.

## 8. Clôture — présenter les commandes
Dis-moi en clair : les fichiers créés, PUIS « Deux commandes sont maintenant disponibles dans ce
projet : `/start` en début de session, `/wrap` en fin. Tape `/start` pour attaquer. » + la 1re étape.

---

### FICHIER start.md  (à écrire dans .claude/commands/start.md)
```
---
description: Début de session — lecture de l'état, situe dans la roadmap, plan.
---
Ouvre la session de travail.

1. Lis `.claude/SESSION.md`, `TODO.md`, `.claude/DEBUG.md` et `ROADMAP.md`
   (`memory/lessons.md` si pertinent).
2. Restitue en 3 lignes max : objectif courant, où on en est, prochaine étape.
3. Situe la session dans les jalons de `ROADMAP.md` : « jalon courant X/N (nom) ».
   Avancement = jalons cochés / total. JAMAIS de pourcentage inventé.
4. Propose un plan priorisé. Attends ma validation explicite avant d'écrire la moindre ligne.

$ARGUMENTS
```

### FICHIER wrap.md  (à écrire dans .claude/commands/wrap.md)
```
---
description: Fin de session — met à jour l'état, coche la roadmap, archive, commit + push.
---
Clôture la session. Dans l'ordre :

1. `.claude/SESSION.md` : copie l'état courant vers `.claude/archive/session-<AAAA-MM-JJ>.md`,
   puis réécris SESSION.md avec le SEUL état courant. Pas d'empilement.
2. `.claude/DEBUG.md` : bugs à jour (résolus avec date / en cours) + nouveaux.
3. `ROADMAP.md` : coche les jalons franchis `- [x]`. Amende la roadmap si besoin — hypothèse révisable.
4. `memory/lessons.md` : leçons de la session. Toute leçon durable → promeus-la en règle dans
   CLAUDE.md et retire-la d'ici.
5. Fichier/dossier créé, renommé ou supprimé → mets à jour l'arbre de `README.md`.
6. Commit par unité logique. Puis push SI un remote existe ; sinon commit local + préviens
   « pas de remote configuré ». (Force-push / suppressions / réécriture d'historique → demander d'abord.)
7. Résume en 2 lignes : fait + première tâche de la prochaine session.

$ARGUMENTS
```