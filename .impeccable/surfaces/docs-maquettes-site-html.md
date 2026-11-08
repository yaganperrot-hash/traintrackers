---
version: 1
slug: "docs-maquettes-site-html"
primary_target: "docs/maquettes/site.html"
related_targets: ["docs/maquettes/aujourdhui.html"]
---

# Surface brief — maquette du site (recherche + page « Aujourd'hui »)

Scope : `docs/maquettes/site.html` (recherche d'un train, mode Operate) et `docs/maquettes/aujourdhui.html`
(bilan du jour, cible des posts X/Instagram). Mobile d'abord (390 px), tutoiement complice.
Tâche : n° de train (+ date, recherche sur 48 h) → gare de descente → verdict → lien officiel.
À éviter (utilisateur) : ressembler à la SNCF, faire « appli bancaire », faire gadget ou ludique.
Décidé : deux pages ; refonte visuelle complète ; corriger les 5 problèmes de la critique du 2026-11-08.
Non résolu : nom du produit (nom de travail « traintracker »).

## Direction contract

THESIS: Le verdict est un reçu qu'on garde : train, gare, retard, droit, imprimés ligne à ligne. Refuse la carte blanche + formulaire bleu des services de réclamation.
OWN-WORLD: Ground gris papier froid, en-tête et boutons encre #1E1F24, reçus blanc thermique à bord cranté, chiffres en mono tabulaire, une seule famille sans pour le reste ; bleu thermique #3B3FA8 réservé au droit ouvert ; retard sur cinq paliers fixes.
STORY: Le voyageur tape son numéro, choisit sa gare, lit « 25 % de ton billet » et clique vers le formulaire officiel ; l'abonné lit le bilan du jour en reçus empilés.
FIRST VIEWPORT: En-tête encre (nom, Aujourd'hui, Aide). Champ n° géant + bouton « Vérifier » au-dessus de la ligne de flottaison ; une fois trouvé, la recherche reste en place (rien ne défile ni ne disparaît au clic) ; le formulaire devient la carte du train (encre), les gares remontent ; téléphone : reçu en tiroir sous la gare touchée ; PC : reçu dans une colonne de droite collante. Essentiel d'abord.
FORM: Le reçu, candidat 6 de ma liste (assigné par le tirage), seed:1b961bc08eb2ae25. Raises : couleur unique du droit (orientation), une famille (annuel), échelle fixe des gares (folio), paliers fixes (exposition). Signature : le reçu qui sort de la fente.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
