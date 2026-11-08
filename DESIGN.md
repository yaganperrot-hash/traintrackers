---
name: traintracker
description: Le verdict de remboursement imprimé comme un reçu thermique (nom de travail, pas une marque).
colors:
  droit: "#3B3FA8"
  ink: "#1E1F24"
  ink-2: "#4A4D55"
  ground: "#E6E8EA"
  paper: "#FAFBFC"
  rule: "#C3C7CC"
  line: "#D8DBDF"
  alerte: "#B3261E"
  attente: "#8A5300"
typography:
  display:
    fontFamily: "Public Sans, system-ui, sans-serif"
    fontSize: "clamp(26px, 6.4vw, 34px)"
    fontWeight: 800
    lineHeight: 1.12
    letterSpacing: "-0.015em"
  verdict:
    fontFamily: "Public Sans, system-ui, sans-serif"
    fontSize: "clamp(28px, 8vw, 36px)"
    fontWeight: 800
    lineHeight: 1.08
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Public Sans, system-ui, sans-serif"
    fontSize: "20px"
    fontWeight: 800
    lineHeight: 1.2
  body:
    fontFamily: "Public Sans, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
  receipt-header:
    fontFamily: "Public Sans, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 800
    letterSpacing: "0.1em"
  receipt-line:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "14px"
    fontWeight: 500
    fontFeature: "tnum"
  receipt-label:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "12px"
    fontWeight: 500
    letterSpacing: "0.04em"
  figure:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "17px"
    fontWeight: 700
    fontFeature: "tnum"
  train-number-input:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: "26px"
    fontWeight: 700
    letterSpacing: "0.04em"
rounded:
  palier: "1px"
  control: "6px"
  segment: "8px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  gutter: "16px"
  section: "28px"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.control}"
    padding: "0 18px"
    height: "48px"
  button-primary-hover:
    backgroundColor: "#000000"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0 18px"
    height: "48px"
  input-field:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0 12px"
    height: "48px"
  input-train-number:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.train-number-input}"
    rounded: "{rounded.control}"
    padding: "0 14px"
    height: "60px"
  receipt:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    padding: "22px 18px 30px"
    width: "460px"
  train-row:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "10px 14px"
    height: "60px"
  segmented:
    backgroundColor: "#D6D9DD"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.segment}"
    padding: "3px"
  segmented-active:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    height: "40px"
  header:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    height: "56px"
---

# Design System: traintracker

## Overview

**Creative North Star: "Le reçu"**

Le verdict est un reçu qu'on garde. Train, date, gare de descente, retard, statut : tout s'imprime ligne à ligne sur un papier thermique blanc, à bord cranté, qui sort d'une fente encre. Le reste de l'interface est un bureau gris froid et sobre, sur lequel le reçu est le seul objet qui compte. Le système refuse la carte blanche et le formulaire bleu des services de réclamation : ici, la réponse est un document, pas un écran de saisie.

La densité est celle d'un ticket de caisse : colonnes étroites (reçu de 460 px au plus), étiquettes en capitales mono à gauche, valeurs alignées à droite, séparateurs en pointillés. Une seule famille sans (Public Sans) porte la voix ; une mono tabulaire (JetBrains Mono) porte les chiffres et les lignes du reçu. La couleur est presque absente : encre, papier, gris. Le seul bleu dit « tu as un droit ».

Rejets confirmés par l'utilisateur : ne jamais ressembler à la SNCF (ni ses couleurs, ni ses logos), pas d'allure d'appli bancaire, rien de gadget ni de ludique.

**Key Characteristics:**
- Le reçu thermique à bord cranté, qui sort d'une fente encre, est la signature.
- Bleu thermique réservé au droit ouvert, et à lui seul.
- Mono tabulaire pour chaque chiffre et chaque ligne de reçu ; Public Sans pour tout le reste.
- Retard toujours lu sur cinq paliers fixes (0, 30, 60, 120, 180 min).
- Un seul mouvement auteur : la sortie du reçu.

## Colors

Une palette d'encre et de papier froid, où une seule couleur saturée a un sens juridique.

### Primary
- **Bleu thermique** (`droit`) : la couleur du droit ouvert. Titre du verdict quand un droit existe (« 25 % de ton billet »), mention « Droit ouvert » ou « Automatique » dans les listes, compteur « Ouvrent un droit » du reçu du jour. Il ne sert à rien d'autre.

### Neutral
- **Encre** (`ink`) : texte principal, en-tête du site, boutons pleins, fente du reçu, paliers allumés sous 30 min.
- **Encre douce** (`ink-2`) : texte secondaire, étiquettes du reçu, légendes, mentions de pied (7.6:1 sur le papier).
- **Gris papier froid** (`ground`) : fond de page, le bureau sur lequel posent les reçus.
- **Papier thermique** (`paper`) : reçus, lignes de train, champs, résumé de recherche, panneau d'aide.
- **Pointillé** (`rule`) : séparateurs en tirets du reçu et entre bandes de la pile.
- **Trait** (`line`) : paliers éteints, bandeau de maquette.

### Signal
- **Rouge alerte** (`alerte`) : train supprimé, retard de 30 min ou plus (chiffre et paliers allumés). Signale le fait, jamais le droit.
- **Ambre attente** (`attente`) : retard de moins de 30 min, chiffre seulement.

### Named Rules
**La règle du bleu unique.** Le bleu thermique signifie « droit ouvert » et rien d'autre : pas de lien, pas de bouton, pas de bandeau, pas de décor. Un écran sans droit ouvert ne montre pas de bleu dans son contenu. L'anneau de focus, le curseur et la sélection sont à l'encre.

**La règle du fait et du droit.** Le rouge dit ce qui est arrivé au train ; le bleu dit ce que le voyageur peut récupérer. Un train supprimé affiche son « Supprimé » en rouge et son « Droit ouvert » en bleu, jamais l'un à la place de l'autre.

## Typography

**Display Font:** Public Sans (avec system-ui, sans-serif)
**Body Font:** Public Sans
**Label/Mono Font:** JetBrains Mono (avec ui-monospace, monospace), chiffres tabulaires

**Character:** Une sans publique, nette et sans affectation, pour parler au voyageur ; une mono d'imprimante pour tout ce qui est relevé, compté ou imprimé. Le passage de l'une à l'autre dit « ceci est un fait mesuré ».

### Hierarchy
- **Display** (800, fluide 26 à 34 px, 1.12) : titre de page, équilibré sur plusieurs lignes.
- **Verdict** (800, fluide 28 à 36 px, 1.08) : la phrase-réponse dans le reçu ; en bleu thermique seulement si un droit est ouvert, en encre sinon.
- **Headline** (800, 20 px, 1.2) : titres de section (« Où es-tu descendu ? », nom du train).
- **Body** (400, 16 px, 1.5) : texte courant et chapô (60 à 65 ch au plus) ; 14 px pour les aides de champ et exemples, 13 px pour les pieds.
- **En-tête de reçu** (800, 13 px, 0.1em, capitales, centré) : le nom du reçu (« Ton verdict », « Le reçu du jour »), en haut du papier uniquement.
- **Ligne de reçu** (mono 500, 14 px) avec **étiquette** (mono 12 px, 0.04em, capitales, encre douce) : paires étiquette / valeur.
- **Chiffre** (mono 700, 17 px) : retard dans les lignes de train ; 22 px pour les compteurs du reçu du jour ; 26 px pour le champ du numéro de train.

### Named Rules
**La règle des deux voix.** Tout chiffre (numéro de train, heure, retard, compteur, pourcentage dans une ligne de reçu) et toute ligne étiquette / valeur du reçu passe en JetBrains Mono tabulaire. Tout le reste, y compris le titre du verdict, est en Public Sans. Pas de troisième famille.

## Layout

Colonne unique, mobile d'abord (conçu à 390 px). Conteneur de page de 680 px au plus, gouttière de 16 px. Le reçu et la fente se centrent dans une colonne plus étroite : fente de 452 px, reçu de 460 px au plus (zone comprise), pour garder la proportion d'un ticket même sur grand écran. Aucun point de rupture : le titre et le verdict utilisent `clamp()`, les grilles de champs passent en `auto-fit` à partir de 200 px.

Rythme vertical : 4 px entre lignes de reçu, 8 à 12 px entre éléments d'une liste, 12 px de marge autour des pointillés, 20 à 28 px entre sections, 48 px en pied de page.

Parcours : la recherche occupe le premier écran (champ du numéro et bouton « Vérifier » au-dessus de la ligne de flottaison) ; une fois le train trouvé, elle se replie en un résumé d'une ligne avec « Modifier », et le reçu prend la place. Le choix d'une gare fait défiler jusqu'au verdict et y place le focus.

## Elevation & Depth

Système presque plat. La profondeur vient du papier posé sur le bureau gris (contraste tonal papier / ground), soutenu par des ombres très douces. Une seule ombre a un rôle structurel : sous la fente, pour que le reçu paraisse en sortir.

### Shadow Vocabulary
- **Fente** (`box-shadow: 0 3px 6px rgba(0,0,0,.25)`) : sous la fente encre uniquement.
- **Papier du reçu** (`box-shadow: 0 2px 8px rgba(30,31,36,.10)`) : le reçu posé.
- **Papier au repos** (`box-shadow: 0 1px 2px rgba(30,31,36,.08)`) : lignes de train et résumé de recherche.
- **Survol** (`box-shadow: 0 0 0 1.5px var(--ink)`) : contour encre au survol d'une ligne cliquable ; 2 px pour la gare sélectionnée.

### Named Rules
**La règle du papier posé.** Rien ne flotte : les surfaces sont du papier sur un bureau. Pas d'ombre portée décalée dure, pas de verre dépoli, pas de carte surélevée au survol ; l'état se marque par un contour encre.

## Shapes

Coins légèrement adoucis (6 px) pour tout ce qu'on touche : boutons, champs, lignes, panneaux. Le sélecteur segmenté a un coin de 8 px à l'extérieur. Les paliers de retard sont des barres quasi droites (1 px). Le reçu, lui, n'a pas de coin arrondi : bords droits en haut (il sort de la fente) et **bord cranté** en bas, découpé par un masque de demi-cercles de 6 px répétés tous les 16 px. La fente est une barre encre de 12 px aux extrémités pleinement arrondies. Les séparateurs du reçu sont des tirets de 1.5 px.

## Components

### Buttons
Encre pleine, directs, sans ornement.
- **Shape :** coins adoucis (6 px), hauteur minimale 48 px (44 px dans le reçu et le résumé).
- **Primary :** fond encre, texte papier, 700, 16 px ; 60 px de haut à côté du champ du numéro.
- **Hover / Focus :** fond noir au survol ; anneau de focus de 3 px décalé de 2 px (blanc dans l'en-tête encre).
- **Secondary :** fond transparent, contour encre intérieur de 1.5 px ; voile encre à 6 % au survol. Pour les suites (« Modifier », « Chercher par gare », « Et maintenant ? »).
- **Lien-bouton :** texte 700 souligné, sans fond, 44 px de cible (« Je n'ai pas mon numéro de train », « Changer de gare »).
- **Lien externe :** l'icône de sortie (SVG trait de 2 px, 1em) reste collée au dernier mot, jamais seule en début de ligne ; le CTA du verdict est pleine largeur, texte centré, et suivi de la mention « Tu quittes le site : on ne transmet rien ».

### Inputs / Fields
- **Style :** papier, trait gris de 1.5 px, coins 6 px, 48 px de haut ; étiquette 700 au-dessus, aide 14 px en encre douce dessous.
- **Champ du numéro de train :** trait encre de 2 px, 60 px de haut, mono 700 26 px espacé, `inputmode="numeric"`.
- **Focus :** le trait passe à l'encre, plus l'anneau de focus global.

### Sélecteur segmenté
- **Style :** rail gris (3 px de marge interne, coins 8 px), options 600 15 px en encre douce, 40 px de haut.
- **État actif :** pastille papier, texte encre, ombre de 1 px. Sert au choix de date et aux onglets de filtre (pleine largeur, trois colonnes égales).

### Lignes de train
- **Style :** bouton papier pleine largeur, 60 px minimum, coins 6 px ; nom du train 700 à gauche, trajet et heure en encre douce dessous, retard en chiffre mono 700 à droite (rouge si ≥ 30 min ou supprimé, ambre sinon).
- **Variante gare :** la colonne de droite (112 px) ajoute les cinq paliers sous le chiffre.

### Navigation
- **Style :** bandeau encre de 56 px, nom du produit 800 17 px à gauche, liens 15 px en gris clair à droite.
- **Actif :** texte blanc et filet blanc de 2 px sous le lien ; survol en blanc. Même rendu sur mobile, sans menu replié.

### Le reçu (composant signature)
La fente encre, puis le papier thermique qui en sort. En haut, l'en-tête de reçu centré ; puis des blocs de lignes étiquette / valeur en mono, séparés par des pointillés ; la ligne « STATUT » donne le résultat (« Droit ouvert », « Pas de droit », « Automatique ») ; puis le verdict en grand, son explication, un exemple chiffré, la règle appliquée, le CTA vers le formulaire officiel et, quand il y en a, les suites « Et maintenant ? » comme vrais boutons à l'intérieur du papier.
- **Mouvement :** à l'apparition, le reçu glisse depuis la fente (`translateY(-100%)` vers 0, 0.7 s, `cubic-bezier(.16, 1, .3, 1)`). Désactivé sous `prefers-reduced-motion`.

### Paliers de retard
Cinq barres égales de 8 px (écart 3 px) pour les seuils fixes 0, 30, 60, 120 et 180 min ; on allume toutes les barres jusqu'au palier atteint. Allumées en encre sous 30 min, en rouge alerte à partir de 30 min ; éteintes en gris trait. Dans le verdict, une légende mono 11 px nomme les seuils. Les paliers sont décoratifs pour les lecteurs d'écran (`aria-hidden`), le chiffre exact étant toujours écrit à côté.

### Pile de reçus (page Aujourd'hui)
Un seul papier sous une fente, découpé en bandes par des pointillés : ligne 1 en mono 700 (train à gauche, retard à droite), trajet et heure dessous, paliers, puis l'état (« Droit ouvert · jusqu'à 25 % » en bleu, ou « Pas de droit · règle » en encre). Au-dessus, le « reçu du jour » porte les compteurs en mono 22 px.

## Do's and Don'ts

### Do:
- **Do** réserver le bleu thermique `#3B3FA8` au seul droit ouvert : titre du verdict, mention d'état, compteur de droits.
- **Do** écrire chaque chiffre et chaque ligne de reçu en JetBrains Mono tabulaire, et tout le reste en Public Sans.
- **Do** lire tout retard sur les cinq paliers fixes 0 / 30 / 60 / 120 / 180 min, avec le chiffre exact à côté.
- **Do** présenter un résultat comme un reçu : fente encre, papier thermique à bord cranté, lignes étiquette / valeur, pointillés, 460 px au plus.
- **Do** garder la sortie du reçu comme seul mouvement auteur, et la couper sous `prefers-reduced-motion`.
- **Do** garder des cibles tactiles de 44 px au moins (48 px pour les boutons et champs principaux).
- **Do** coller l'icône de lien externe au dernier mot du libellé.

### Don't:
- **Don't** imiter la SNCF : ni ses couleurs, ni ses logos, ni sa typographie, ni ses pictogrammes.
- **Don't** prendre l'allure d'une appli bancaire : pas de cartes dégradées, de grands soldes en couleur, de tableaux de bord à jauges.
- **Don't** faire gadget ou ludique : pas de confettis, d'animation de célébration, de mascotte, de compteur qui défile.
- **Don't** utiliser le bleu thermique pour un lien, un bouton, un bandeau, un état de focus ou un décor.
- **Don't** inventer de paliers intermédiaires ni une jauge continue de retard.
- **Don't** poser un sur-titre ou une étiquette en capitales au-dessus d'un titre de page ; les capitales espacées vivent seulement dans l'en-tête et les étiquettes du reçu.
- **Don't** ajouter d'autre mouvement que la sortie du reçu.
