# Stratégie de communication — monretard.fr

> Rédigée le 2026-11-11. Document de travail : rien ici n'est encore mis en œuvre.
> ⚠️ = affirmation à vérifier à la source avant d'agir (règle budget et quotas de `CLAUDE.md`).

## Cadre retenu (réponses du 2026-11-11)

- **Incarnation** : anonyme, la marque seule (« monretard.fr »).
- **Temps disponible** : 2 à 4 h par semaine, publication du post quotidien comprise.
- **Canaux** : X, Instagram, TikTok / Reels, Bluesky / Threads / Mastodon, Reddit et forums.
- **Objectif à 6-12 mois** : utilité publique et audience. Pas de monétisation.
- **Contraintes du projet** : aucune dépense hors VPS, Claude et domaine ; aucune API payante ;
  aucune donnée personnelle ; publication X et Instagram à la main.

## Constat de départ

Sur les requêtes « retard train remboursement », Google ne renvoie que des guides généraux
(SNCF Connect, Que Choisir, Routard, Selectra, AirHelp). Dans les recherches du 2026-11-11, aucun
résultat ne répond à « mon train n° X d'hier ouvre-t-il droit à quelque chose ? ».

**Positionnement** : la réponse par train et par jour, avec la règle applicable et le lien officiel.
Les données sont le contenu ; tout le reste (posts, pages, chiffres pour la presse) en découle
automatiquement.

## 1. Avant d'ouvrir au public

- [ ] Réserver monretard.fr (libre au registre AFNIC le 2026-11-08) et vérifier la marque à l'INPI.
- [ ] Créer les comptes sur les six plateformes avec le même identifiant.
- [ ] Tester le nom : « retard » est une insulte en anglais. Vérifier à la création que l'identifiant
      passe sur TikTok et Instagram ; prévoir un nom de repli.
- [ ] Trancher les trois décisions en attente de `TODO.md` (type inconnu supprimé, tutoiement,
      TGV INOUI international). Un 75 % affiché au lieu de 50 %, repris en capture d'écran, ruine la
      crédibilité.
- [ ] Trois pages de confiance : « Méthode et sources », « Qui sommes-nous » (indépendant, non affilié
      à la SNCF, gratuit, sans données personnelles), page presse avec une adresse de contact au nom
      du domaine.
- [ ] Mentions légales en restant anonyme : la loi (LCEN) le permet en principe à un éditeur non
      professionnel qui indique son hébergeur ⚠️ à vérifier sur Légifrance.
- [ ] Ne pas utiliser les logos ni la charte de la SNCF et des autres opérateurs.

## 2. Google — canal principal à long terme

- **Une page indexable par train et par jour** (« TGV 6607 du 10 novembre 2026 : 47 min de retard,
  25 % »). Les voyageurs tapent leur numéro de train ; la conservation illimitée construit des
  milliers de pages.
- **Des pages par ligne et par gare** (« retards Paris–Lyon », « retards gare de Rennes ») avec les
  statistiques (jalon 8).
- **Un guide par règle** (G30, OUIGO, Eurostar, Trenitalia, chaque région TER), daté et sourcé, à
  partir de `docs/regles-remboursement.md`.
- **HTML rendu côté serveur** : une page remplie en JavaScript est vue vide par beaucoup de robots.
  À vérifier sur le front actuel (`frontend/aujourdhui.html` appelle `/api/aujourdhui` côté navigateur).
- **Technique gratuite** : sitemap, données structurées (FAQ, fil d'Ariane), Google Search Console,
  Bing Webmaster Tools.

## 3. IA (ChatGPT, Claude, Perplexity, Gemini)

Les IA citent ce qui est factuel, daté, sourcé et repris ailleurs.

- Autoriser leurs robots dans `robots.txt` (GPTBot, ClaudeBot, PerplexityBot, Google-Extended).
- Réponse directe en tête de chaque guide (« Un TGV INOUI en retard de 30 min à 2 h donne droit à
  25 % »), avec la date de vérification.
- Publier le jeu de données en open data et le déclarer comme réutilisation sur
  transport.data.gouv.fr. La licence ODbL du flux impose de toute façon l'attribution ; on y gagne
  un lien depuis un site public.
- Être cité ailleurs : Reddit, presse et forums pèsent dans les réponses des IA. Bing compte aussi.

## 4. Réseaux sociaux

| Canal | Ce qu'on y fait | Effort |
|---|---|---|
| X | Post quotidien ; réponses utiles aux voyageurs les jours de grosse perturbation | Manuel |
| Instagram | Carrousel quotidien, story, un Reel par semaine | Manuel |
| TikTok / Reels | Une vidéo sans visage par semaine, générée depuis les données (« le pire train de la semaine ») | 30 à 45 min |
| Bluesky, Mastodon | Même post que X, automatisable | Nul une fois codé |
| Threads | Même post, à la main au début | 2 min |
| Reddit | Un post de lancement, puis réponses aux questions sur les retards | 30 min / semaine |

- L'adresse figure sur chaque image (décision du 2026-11-08) ; le lien va en réponse ou en bio
  plutôt que dans le post.
- Formats qui se partagent : classement hebdomadaire, « train du jour », carte des retards. La simple
  liste quotidienne informe mais circule peu.
- Automatisation ⚠️ : l'API Bluesky est décrite comme gratuite dans sa documentation ; celle de
  Threads comme gratuite mais soumise à validation Meta ; Mastodon non vérifié. À confirmer à la
  source avant tout code.
- Reddit : lire les règles d'autopromotion de chaque communauté avant de poster.

## 5. Presse

Sans personne à citer, c'est le chiffre qui fait l'article.

- **Baromètre mensuel** : nombre de trains ouvrant droit à indemnisation, pires lignes, pires jours,
  par région. Une page publique et un court communiqué.
- **Presse régionale d'abord** : un chiffre local est repris plus facilement qu'un chiffre national.
- **Ensuite** : presse conso (60 Millions de consommateurs, Que Choisir, Capital, Le Parisien),
  presse tech (Next, Numerama), associations d'usagers (FNAUT).
- **Bons moments** : grèves, départs en vacances, intempéries, bilans annuels de ponctualité. Envoyer
  le chiffre le jour même.
- **Précédent** : Skotovoz, suivi de trains tenu par une seule personne, a obtenu un article parce que
  la SNCF ne fournissait pas les chiffres.
- **Limite de l'anonymat** : les journalistes voudront un interlocuteur. Un prénom ou un pseudonyme
  constant et une adresse de contact suffisent en général.

## 6. Calendrier

1. **Fondations** (jusqu'à la mise en ligne) : domaine, comptes, règles tranchées, pages de confiance,
   pages indexables.
2. **Rodage** (4 semaines) : post quotidien partout, sans annonce. On corrige avant d'avoir du public.
3. **Lancement** : post Reddit, presse tech, jeu de données publié.
4. **Croisière** : baromètre mensuel, presse régionale, vidéo hebdomadaire.
5. **Pics** : chaque grève ou grosse panne est une fenêtre ; réaction dans l'heure sur X.

Temps hebdomadaire : environ 1 h de publication, 45 min de réponses (X, Reddit), 45 min de vidéo,
30 min de presse.

## 7. Mesure

- Clics et impressions dans Search Console.
- Visites comptées depuis les journaux du serveur, sans cookie.
- Abonnés par canal.
- Reprises presse.
- Visites venant des IA.

## Ce que la stratégie demande au code (à planifier, rien de décidé)

- Pages indexables par train et par jour, par ligne, par gare ; rendu côté serveur ; sitemap.
- Guides par règle, pages de confiance, mentions légales.
- Baromètre mensuel (dépend du jalon 8, statistiques).
- Visuels et vidéos générés (dépend du jalon 4, post quotidien).
- Publication automatique Bluesky / Mastodon, après vérification des conditions à la source.
- Export open data du jeu de données.

## Sources (consultées le 2026-11-11)

- SNCF Connect — retard et remboursement : https://www.sncf-connect.com/aide/retard-de-votre-train-et-remboursement
- Que Choisir — droits des passagers : https://www.quechoisir.org/conseils-train-les-droits-des-passagers-n168240/
- Routard — retard et annulation : https://www.routard.com/dossiers-pratiques/cid136122-train-retard-et-annulation-quels-sont-vos-droits.html
- AirHelp — remboursement SNCF : https://www.airhelp.fr/blog/remboursement-sncf-pour-retard-ou-annulation/
- Selectra — G30 : https://selectra.info/assurance/actualites/marche/retard-tgv-intercites-g30-toussaint-remboursement
- Skotovoz (Luxtoday) : https://luxtoday.lu/fr/transports-et-infrastructures/bienvenue-chez-skotovoz-fr
- SNCF — open data : https://www.groupe-sncf.com/en/commitments/open-data
- Bluesky — limites d'API : https://docs.bsky.app/docs/advanced-guides/rate-limits
- Meta — API Threads : https://developers.facebook.com/documentation/threads
