# Règles de remboursement — veille (jalon 2)

> **Statut : brouillon à valider** (zone critique). Rien ne s'encode avant validation.
> Veille du 2026-11-07. Chaque ligne cite sa source ; ✅ = lu sur une source officielle de l'opérateur
> ou du législateur, ⚠️ = source secondaire ou contradictions, à confirmer.
> Les pages `tgvinoui.sncf` et `sncf-voyageurs.com` refusent la lecture automatique (HTTP 403) :
> la G30 est lue via SNCF Connect, à recouper à la main.

## Synthèse

| Train (code flux) | Seuil | Barème | Forme | Démarche | Délai | Statut |
|---|---|---|---|---|---|---|
| TGV INOUI national (`OUI`), Intercités (`IC`, `ICN`) — G30 | 30 min | 30–119 min : 25 % · 120–179 : 50 % · ≥180 : 75 % | < 1 h : bon d'achat ; ≥ 1 h : virement (bon seulement si accord exprès) | Formulaire SNCF Voyageurs | 90 j ⚠️ | ✅ barème / ⚠️ délai |
| TGV INOUI international (dont Lyria `LYR`, France-Italie, France-Espagne) | 30 min | 30–119 : 25 % · ≥120 : 50 % (plafond 50 %) | idem G30 | Formulaire SNCF Voyageurs | ⚠️ | ✅ |
| OUIGO (`OGO`) | 60 min | 60–119 : 25 % · ≥120 : 50 % | Bon d'achat **automatique** (e-mail), remboursable en numéraire pendant sa validité (6 mois) | **Aucune** : automatique. Sans bon sous 15 j → service client | 90 j | ✅ CGTV V71 (03/2026) |
| Trenitalia France (Paris–Lyon–Milan, Paris–Marseille) | 30 min | 30–59 : 25 % (geste commercial) · 60–119 : 25 % · ≥120 : 50 % | Bon d'achat digital (≥ 60 min : forme à confirmer ⚠️) | Formulaire / auto-remboursement Trenitalia France | 12 mois | ✅ seuils / ⚠️ forme |
| Eurostar | 60 min | 60–119 : 25 % cash ou 30 % e-voucher · 120–179 : 50 % / 60 % · ≥180 : 50 % / 75 % | cash ou e-voucher (12 mois) | « Gérer ma réservation » Eurostar | 3 mois (attendre 24 h) | ✅ |
| ICE / Deutsche Bahn (`ICE`) | 60 min | 60–119 : 25 % · ≥120 : 50 % ; versé si > 4 € | bon, guichet ou virement | Formulaire DB | 90 j | ✅ (via SNCF Connect) |
| CFF (Suisse) | 60 min | 60–119 : 25 % · ≥120 : 50 % ; versé si > 5 CHF | — | Formulaire CFF | 90 j | ✅ (via SNCF Connect) |
| Renfe (Lyon–Barcelone, Marseille–Madrid) | 60 min ⚠️ | 60–89 : 50 % · ≥90 : 100 % ⚠️ | — | Site Renfe | ⚠️ | ⚠️ sources contradictoires |
| TER (`TER`, `CTE`, `TT`, `NAV`…) | selon région | Rien pour un occasionnel dans 8 régions ; garanties en Normandie (Nomad Résa), Centre-Val de Loire (Rémi), Pays de la Loire (suppressions) | — | Service client régional + bulletin de retard | — | ⚠️ voir § TER par région |

**Plancher légal (règlement UE 2021/782, art. 19)** ✅ : 25 % à 60–119 min, 50 % à ≥ 120 min, sur le prix payé ;
seuil de non-versement ≤ 4 € par billet ; payé sous un mois, en espèces si le voyageur le demande ;
exonération si circonstances extraordinaires extérieures à l'exploitation (météo extrême, catastrophe,
crise sanitaire majeure, faute du voyageur, certains tiers) — **la grève du personnel de l'opérateur
n'exonère pas**. Les garanties commerciales (G30, Trenitalia 30–59 min) vont au-delà.

## Points qui changent la conception — à trancher

1. **Le retard se mesure à l'arrivée du voyageur, pas au terminus du train.** Un voyageur qui
   descend avant le terminus peut avoir un retard différent. Conséquences :
   - **Site** : la recherche doit demander la gare d'arrivée (on a le retard arrêt par arrêt).
   - **Post quotidien** : lister les trains « ≥ seuil au terminus » est une approximation. Proposition :
     lister les trains ayant dépassé le seuil **à au moins un arrêt**, en précisant « selon votre gare
     d'arrivée ».
2. **Seuils différents selon le train** : 30 min (G30, Trenitalia) ou 60 min (Ouigo, Eurostar, DB, CFF,
   Renfe). Le produit dans le `trip_id` du flux suffit à choisir la règle.
3. **OUIGO est automatique** : pas de lien de demande ; le message utile est « vérifiez votre e-mail,
   sinon contactez le service client sous 15 jours ».
4. **On ne peut afficher que des pourcentages**, pas des montants : le prix du billet est inconnu.
5. **TER** : en France, les services régionaux sont exemptés des articles d'indemnisation du règlement
   (dérogation, code des transports L2151-2 ⚠️). **Décidé le 2026-11-07** : les TER restent affichés,
   avec la règle de leur région. ⚠️ **Mais « TER = aucun remboursement » est faux pour 3 régions**
   (voir § TER par région) : le message doit dépendre de la région, et parfois du type de train.
6. **Suppressions** — voir § Suppressions.
7. **Trajets avec correspondance** — voir § Correspondances. Proposition : hors v1 (on raisonne par
   train), avec un encart explicatif.
8. **Couverture du flux** : Eurostar et Renfe absents du GTFS-RT SNCF au premier relevé. Si le POC le
   confirme, leurs règles restent documentées mais inutilisables sans autre source.

## TER par région — voyageurs occasionnels (veille 2026-11-07)

Les pages ter.sncf.com refusent la lecture automatique (403) : contenus lus via extraits de moteur de
recherche, **tous ⚠️ à confirmer à la main**. Plusieurs pages ont plusieurs années.

| Région | Garantie occasionnels | Règle | Lien |
|---|---|---|---|
| Normandie (Nomad) | **Oui, trains Nomad Résa** (réservation obligatoire) | ≥ 30 min : 25 % · ≥ 2 h : 50 % · ≥ 3 h : 75 % ; suppression inopinée ; bon d'achat ≥ 4 € ; demande sous 30 j | https://www.ter.sncf.com/normandie/services-contacts/sav/garantie-voyageurs-occasionnels |
| Centre-Val de Loire (Rémi) | **Oui** | Rémi Express : ≥ 30 min (25 % → 75 %) ; Rémi train : ≥ 60 min ; bon d'achat ; seuil 4 € ; 90 j ; trajets sans correspondance | https://www.ter.sncf.com/centre-val-de-loire/services-contacts/garantie-ponctualite-remi-express |
| Pays de la Loire (Aléop) | **Oui, suppressions seulement** | Train supprimé sans solution de report sous 30 min : 100 % du billet en bon d'achat Aléop ; trajet interne, train uniquement ; J+1 à 30 j | https://www.ter.sncf.com/pays-de-la-loire/services-contacts/garantie-ponctualite-occasionnels |
| Occitanie (liO) | Non (sans correspondance) | Avec correspondance (billet direct) et ≥ 60 min : indemnisation possible | https://www.ter.sncf.com/occitanie/services-contacts/contacts/information-reclamation |
| Grand Est (Fluo) | Au cas par cas | Réclamation au service client, « indemnisation en fonction de l'examen du dossier » | https://www.ter.sncf.com/grand-est/services-contacts/questions-reponses |
| Auvergne-Rhône-Alpes | Non | Bulletin de retard dès 5 min (justificatif seulement) | https://www.ter.sncf.com/auvergne-rhone-alpes/services-contacts/bulletin-retard |
| Bourgogne-Franche-Comté (Mobigo) | Non | « Pas de garantie ponctualité sur TER » ; engagement réservé aux abonnés | https://www.ter.sncf.com/bourgogne-franche-comte/services-contacts/engagement-ponctualite/abonnement-illimite-pass-mobigo |
| Bretagne (BreizhGo) | Non | Billet valable la journée (prendre un autre train) ; bulletin de retard | https://www.ter.sncf.com/bretagne/services-et-contacts/questions-reponses |
| Hauts-de-France | Non (abonnés seulement) | Abonnés : 20 % de la mensualité après 11 perturbations ≥ 10 min dans le mois | https://www.ter.sncf.com/hauts-de-france/services-et-contacts/garantie-ter-hauts-de-france-v1 |
| Nouvelle-Aquitaine | Non (abonnés seulement) | Abonnés : 20 / 30 / 40 % après 8 retards ou suppressions > 15 min par mois | https://www.ter.sncf.com/nouvelle-aquitaine/garantie-fiabilite |
| Sud PACA (ZOU) | Inconnu pour les occasionnels | Abonnés : 30 % après 8 perturbations ≥ 15 min dans le mois | https://www.ter.sncf.com/sud-provence-alpes-cote-d-azur/services-contacts/garantie-fiabilite |

**Conséquences pour le code** : il faut connaître la **région** de chaque TER (via la ligne / l'agence
du GTFS, ou les gares) et, pour la Normandie et le Centre-Val de Loire, le **type de train**
(Nomad Résa / Krono, Rémi Express / Rémi).
Vérifié le 2026-11-07 : le GTFS **ne porte ni la région ni la marque** (une seule agence « SNCF
VOYAGEURS », aucun nom Nomad / Rémi / Krono dans les lignes). Pistes : région déduite des coordonnées
des gares (polygones des régions, open data) ; type de train à partir de listes de lignes / numéros
publiées par les régions. À traiter au jalon 2 (encodage).

## Suppressions (règlement UE 2021/782, art. 18 et 19 ✅ ; pratiques SNCF ⚠️)

- **Train supprimé ou arrivée prévue ≥ 60 min en retard** (art. 18) : le voyageur choisit entre
  remboursement intégral (sous 30 jours), réacheminement au plus tôt, ou voyage à une date ultérieure,
  sans surcoût. Sans proposition de réacheminement dans les **100 min**, il peut réserver lui-même
  (train, car, bus) et se faire rembourser les frais raisonnables.
- **Pas de cumul** : l'indemnisation de l'art. 19 ne s'applique que si le voyageur n'a pas été remboursé
  au titre de l'art. 18. S'il voyage quand même (train suivant, substitution), c'est son **retard à
  l'arrivée** qui compte (G30 ou art. 19 selon le train).
- **Chez SNCF** ⚠️ : remboursement intégral du billet, y compris tarifs promo, **non automatique** (à
  demander via SNCF Connect, l'agence ou le 3635). Exception TER : billet en général valable la journée.
- **TER** : la dérogation française s'applique aussi aux droits de l'art. 18 ⚠️ à confirmer ; voir les
  garanties régionales ci-dessus (Pays de la Loire, Normandie).
- **Message site/post proposé** : « Train supprimé : vous pouvez demander le remboursement intégral de
  votre billet. Si vous avez pris un autre train, votre droit dépend de votre retard à l'arrivée. »

## Correspondances (art. 12 ✅)

- Billets achetés **en une seule transaction auprès d'un même opérateur** = billet direct : l'opérateur
  est responsable de la correspondance manquée (art. 18, 19, 20) ; le retard se mesure à la
  destination finale.
- Billets combinés par un **revendeur** de sa propre initiative : remboursement total + **75 %**
  d'indemnisation en cas de correspondance manquée (sous 30 jours), sauf si les billets étaient
  présentés comme contrats séparés.
- SNCF : formulaire unique pour TGV INOUI + TER (https://tout-oui.sncf.com/). OUIGO : seul le train en
  retard est pris en compte.
- **Proposition v1** : on raisonne par train ; un encart explique que pour une correspondance, c'est
  le retard à la destination finale du billet qui compte.

## Liens de demande

- G30 (TGV INOUI, Intercités, internationaux SNCF) :
  https://www.sncf-voyageurs.com/fr/contactez-nous/demande-et-reclamation/?path=%2FTR&stepCode=TR_D1
- Correspondance TGV INOUI + TER : https://tout-oui.sncf.com/
- TER (par région) : https://www.sncf-voyageurs.com/fr/contactez-nous/en-cas-de-retard/ter-transilien/
- OUIGO (si pas de bon reçu) : https://www.ouigo.com/contact
- Trenitalia France : https://trenitalia.fr/informations/faire-une-demande-indemnisation/
- Eurostar : https://www.eurostar.com/fr-fr/voyage/informations-trafic/politique-de-compensation
- Deutsche Bahn : https://int.bahn.de/fr/aide/contact/formulaires
- CFF : https://www.sbb.ch/fr/aide-et-contact/service-clientele/critiques-compliments/reclamations.html

## Sources

- SNCF Connect — Retard d'un train et remboursement (barèmes par type de train, consulté 2026-11-07) :
  https://www.sncf-connect.com/aide/retard-de-votre-train-et-remboursement
- Règlement (UE) 2021/782, art. 2 et 19 (EUR-Lex) :
  https://eur-lex.europa.eu/legal-content/FR/TXT/HTML/?uri=CELEX:32021R0782
- OUIGO — Conditions de transport et de vente V71 (24/03/2026) :
  https://cdn-fr.ouigo.com/edito-p-v3-assets/2026-03/24-03-2026_CGTV%20V71%20OUIGO.pdf
- Trenitalia France — Vos droits en cas de retard : https://trenitalia.fr/assistance/vos-droits-en-cas-de-retard/
- Trenitalia — Indemnités en cas de retard (lignes italiennes) :
  https://www.trenitalia.com/fr/information/les-indemnites-encasderetard.html
- Eurostar — Politique de compensation :
  https://www.eurostar.com/fr-fr/voyage/informations-trafic/politique-de-compensation
- FNAUT — Droits des voyageurs en cas de retard ou suppression (dérogation TER) ⚠️ 2022 :
  https://www.fnaut.fr/uploads/2022/11/Fiche-droits-des-voyageurs-en-cas-de-retard-ou-suppression-de-trainsV7.2.pdf
- TER Pays de la Loire — Garantie ponctualité abonnés ⚠️ :
  https://www.ter.sncf.com/pays-de-la-loire/services-contacts/garantie-ponctualite-abonnes
- TER Sud — Garantie fiabilité ⚠️ : https://www.ter.sncf.com/sud-provence-alpes-cote-d-azur/services-contacts/garantie-fiabilite
- Renfe ⚠️ : https://lepetitjournal.com/vivre-a-valence/retard-train-renfe-comment-se-faire-indemniser-358162 ,
  https://www.voyagerentrain.fr/retard-train-remboursement/

## Reste à faire avant encodage

- [ ] Recouper la G30 sur tgvinoui.sncf / sncf-voyageurs.com (lecture manuelle : 403 en automatique), dont le délai de 90 j.
- [ ] Forme d'indemnisation Trenitalia France ≥ 60 min (bon seul ou numéraire).
- [ ] Barème Renfe en vigueur.
- [x] TER : garanties des 11 régions du flux (2026-11-07, toutes ⚠️ à confirmer à la main).
- [ ] TER : confirmer la dérogation française (code des transports L2151-2) et son effet sur l'art. 18.
- [x] TER : le GTFS ne donne ni région ni marque (2026-11-07) → région par coordonnées des gares.
- [ ] TER : identifier les trains Nomad Résa (Normandie) et Rémi Express (Centre-Val de Loire).
- [x] Règles « suppression » et « correspondance » (art. 12, 18, 19 lus sur EUR-Lex).
