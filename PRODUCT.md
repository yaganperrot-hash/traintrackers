# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Deux publics, à égalité (confirmé le 2026-11-08) :

- **Le voyageur concerné** : son train était en retard ou supprimé. Souvent au téléphone, en gare ou
  rentré chez lui le soir ou le lendemain. Il veut savoir en quelques secondes s'il a droit à un
  dédommagement, combien, et où faire la demande.
- **Les abonnés des réseaux** (X, Instagram) : ils arrivent par le lien du post quotidien et consultent
  le bilan du jour (trains ouvrant droit, supprimés, en retard), puis éventuellement leur train.

## Product Purpose

Suivre le réseau SNCF en temps réel, calculer retards et suppressions, et dire clairement quels trains
ouvrent droit à un remboursement, avec le lien vers le formulaire officiel. Succès : un post quotidien
et un site qui marchent. Le site ne dépose jamais de demande à la place du voyageur.

## Positioning

Le droit est calculé **à la gare où le voyageur est descendu**, pas au terminus, avec la règle propre à
chaque type de train (G30, OUIGO automatique, TER par région, Krono+ Normandie, Rémi Express…). Un train
absent ou sans droit est toujours expliqué, pour qu'un visiteur ne croie jamais à un bug.

## Operating Context

- Données : flux temps réel SNCF (GTFS-RT, rafraîchi toutes les 2 min) et horaires officiels (GTFS),
  open data ODbL via transport.data.gouv.fr. Historique conservé (stats futures).
- Parcours principal : numéro de train → date → gare de descente → verdict → lien de demande officiel.
- Le post quotidien (texte + image) est généré par le système et publié **à la main** sur X et Instagram.
- Règles d'éligibilité : `docs/regles-remboursement.md` (validé), encodées dans `backend/regles.py`.

## Capabilities and Constraints

- Périmètre : TGV INOUI, Intercités, OUIGO, TER, Lyria, ICE et autres internationaux du flux.
  Hors périmètre : RER, métro, Transilien. Eurostar et Renfe absents du flux à ce jour.
- On affiche des **pourcentages** du prix du billet, jamais de montant (prix inconnu).
- Aucune donnée personnelle, aucun compte utilisateur.
- Stack : FastAPI + PostgreSQL ; frontend HTML/CSS/JS vanilla, une page par vue.
- Budget : aucune API ni service payant en dehors du VPS, de Claude et du domaine.
- Termes du voyageur : « retard », « supprimé », « dédommagement », « bon d'achat », « virement »,
  « gare d'arrivée ». « G30 » est un terme SNCF à expliquer quand il apparaît.

## Brand Commitments

- **Nom : à définir.** « traintracker » est un nom de travail, pas une marque : ne pas construire
  d'identité autour.
- **Ton : tutoiement, complice** (choisi le 2026-11-08). Direct et familier, proche des réseaux
  sociaux, mais les faits restent exacts et sourcés : on ne promet jamais un droit incertain.
- Site indépendant, non affilié à la SNCF : ne jamais imiter la marque, les couleurs ou les logos SNCF.

## Evidence on Hand

- Données réelles collectées par le POC (`poc/data/`, non versionné) ; rapport du 2026-11-07.
- Aucun témoignage, chiffre d'audience, partenaire ou presse : ne pas en inventer.
- Les textes marqués ⚠️ dans `docs/regles-remboursement.md` restent à confirmer avant publication.

## Product Principles

1. **Une réponse, pas un tableau** : le voyageur obtient son verdict pour sa gare en quelques secondes.
2. **Jamais de vide inexpliqué** : chaque « non » et chaque train introuvable dit pourquoi et propose
   une suite.
3. **Exact avant d'être engageant** : chaque règle cite sa source ; le doute s'affiche « à confirmer ».
4. **On renvoie vers l'officiel** : le site dit où faire la demande et ne transmet rien.

## Accessibility & Inclusion

Usage mobile d'abord, à une main. Cibles tactiles d'au moins 44 px, contraste WCAG AA, parcours
complet au clavier et au lecteur d'écran.
