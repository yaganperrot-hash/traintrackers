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
| TER (`TER`, `CTE`, `TT`, `NAV`…) | — | Pas de droit par train généralisé : politiques régionales, surtout pour **abonnés** (cumul mensuel) | — | Service client régional + bulletin de retard | — | ⚠️ voir § TER |

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
   (dérogation, code des transports L2151-2 ⚠️). Les garanties régionales visent surtout les abonnés
   (ex. Pays de la Loire : 20 % du forfait après 8 retards > 10 min dans le mois ; Sud : 30 % de la
   mensualité après 8 retards/suppressions ⚠️ pages anciennes). Pour un voyageur occasionnel, il n'y a en
   général **aucun droit par train**. → Décision produit : afficher les TER (retards, suppressions) sans
   promettre de remboursement, avec un lien vers la garantie de la région ? Ou les sortir du post ?
6. **Suppressions** : droits distincts (remboursement intégral ou réacheminement, assistance) ; la G30
   s'applique si le train de substitution arrive ≥ 30 min en retard ⚠️. À détailler avant encodage.
7. **Trajets avec correspondance** : règles spécifiques (formulaire unique TGV + TER, Ouigo : seul le
   train en retard compte). Hors périmètre de la v1 ? À décider.
8. **Couverture du flux** : Eurostar et Renfe absents du GTFS-RT SNCF au premier relevé. Si le POC le
   confirme, leurs règles restent documentées mais inutilisables sans autre source.

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
- [ ] TER : garanties des 11 régions du flux, et confirmation de la dérogation française.
- [ ] Règles « suppression » et « correspondance ».
