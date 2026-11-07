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


