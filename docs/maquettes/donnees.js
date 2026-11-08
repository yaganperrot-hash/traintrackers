// Données FICTIVES de la maquette (numéros, gares, retards et causes inventés).
// droit() est un reflet simplifié de backend/regles.py ; le vrai site appellera l'API.
"use strict";

const AUJOURDHUI = "2026-11-08";
const HIER = "2026-11-07";

const TRAINS = [
  { date: AUJOURDHUI, prod: "TGV INOUI", num: "6611", h: "08:07", cause: "Panne de signalisation", regle: "g30",
    gares: [["Paris Gare de Lyon", 0], ["Avignon TGV", 52], ["Aix-en-Provence TGV", 68], ["Marseille Saint-Charles", 74]] },
  { date: AUJOURDHUI, prod: "OUIGO", num: "7815", h: "09:42", cause: "Obstacle sur la voie", regle: "ouigo",
    gares: [["Marne-la-Vallée Chessy", 0], ["Lyon Saint-Exupéry", 55], ["Nîmes Pont-du-Gard", 118], ["Montpellier Sud de France", 128]] },
  { date: AUJOURDHUI, prod: "TER", num: "17742", h: "07:15", cause: "Difficultés lors de la préparation du train", regle: "ter-none", region: "Auvergne-Rhône-Alpes",
    gares: [["Lyon Part-Dieu", 0], ["Bourgoin-Jallieu", 38], ["Grenoble", 41]] },
  { date: AUJOURDHUI, prod: "Intercités", num: "3621", h: "10:01", cause: "Ralentissement : travaux", regle: "g30",
    gares: [["Paris Austerlitz", 0], ["Orléans", 12], ["Limoges-Bénédictins", 28], ["Brive-la-Gaillarde", 33]] },
  { date: AUJOURDHUI, prod: "TER Krono+", num: "3115", h: "11:20", cause: "Panne de matériel", regle: "ter-krono", region: "Normandie",
    gares: [["Paris Saint-Lazare", 0], ["Rouen Rive Droite", 31], ["Le Havre", 36]] },
  { date: AUJOURDHUI, prod: "Intercités", num: "4756", h: "07:20", cause: "Mouvement social", regle: "g30", supprime: true,
    gares: [["Bordeaux Saint-Jean", 0], ["Toulouse Matabiau", 0], ["Montpellier Saint-Roch", 0], ["Marseille Saint-Charles", 0]] },
  { date: AUJOURDHUI, prod: "TGV INOUI", num: "8521", h: "12:05", cause: "Affluence de voyageurs", regle: "g30",
    gares: [["Paris Montparnasse", 0], ["Le Mans", 15], ["Rennes", 18]] },
  { date: AUJOURDHUI, prod: "Lyria", num: "9765", h: "13:10", cause: "Panne d'un aiguillage", regle: "g30-int",
    gares: [["Paris Gare de Lyon", 0], ["Bellegarde", 47], ["Genève", 52]] },
  { date: HIER, prod: "TGV INOUI", num: "6203", h: "18:52", cause: "Accident de personne", regle: "g30",
    gares: [["Paris Montparnasse", 0], ["Poitiers", 121], ["Angoulême", 128], ["Bordeaux Saint-Jean", 135]] },
  { date: HIER, prod: "TGV INOUI", num: "6611", h: "08:07", cause: "Défaut d'alimentation électrique", regle: "g30",
    gares: [["Paris Gare de Lyon", 0], ["Avignon TGV", 9], ["Aix-en-Provence TGV", 14], ["Marseille Saint-Charles", 21]] },
];

const LIENS = {
  g30: ["Faire ma demande sur SNCF Voyageurs", "https://www.sncf-voyageurs.com/fr/contactez-nous/demande-et-reclamation/"],
  ouigo: ["Contacter OUIGO", "https://www.ouigo.com/contact"],
  krono: ["Faire ma demande sur TER Normandie", "https://www.ter.sncf.com/normandie/services-contacts/sav/garantie-voyageurs-occasionnels"],
  ter: ["Voir la garantie de la région", "https://www.sncf-voyageurs.com/fr/contactez-nous/en-cas-de-retard/ter-transilien/"],
};
const SUITE_STANDARD = [
  { texte: "Tu avais une correspondance avec un billet unique ? C'est le retard à ta destination finale qui compte.",
    action: "Chercher mon dernier train" },
  { texte: "Abonné ? Ta région prévoit peut-être une compensation mensuelle.",
    action: "Voir les compensations TER", lien: LIENS.ter[1] },
];

const palier = (r, paliers) => paliers.reduce((p, [s, v]) => (r >= s ? v : p), null);
// Index du palier fixe : 0 = moins de 30, 1 = 30, 2 = 60, 3 = 120, 4 = 180 min et plus
const indexPalier = (r) => (r >= 180 ? 4 : r >= 120 ? 3 : r >= 60 ? 2 : r >= 30 ? 1 : 0);
const exemple = (pct) => `Sur un billet à 80 €, ça fait ${Math.round(80 * pct / 100)} €.`;

function droit(t, r) {
  if (t.supprime) return { ton: "ok", tampon: "Droit ouvert", titre: "Remboursement intégral",
    texte: "Ton train a été supprimé : tu peux demander le remboursement de ton billet.",
    forme: "Remboursement", regle: "Train supprimé", lien: t.regle === "ouigo" ? LIENS.ouigo : LIENS.g30,
    suite: [{ texte: "Tu as pris un autre train ? Ton droit dépend alors de ton retard à l'arrivée.", action: "Chercher ce train" }] };
  if (t.regle === "g30" || t.regle === "g30-int") {
    if (r < 30) return { ton: "none", tampon: "Pas de droit", titre: "Pas de dédommagement",
      texte: "Moins de 30 min de retard à ta gare. La garantie G30 (la compensation SNCF des TGV INOUI et Intercités) démarre à 30 min.",
      regle: "Garantie G30", suite: SUITE_STANDARD };
    const pct = palier(r, t.regle === "g30-int" ? [[30, 25], [120, 50]] : [[30, 25], [120, 50], [180, 75]]);
    return { ton: "ok", tampon: "Droit ouvert", titre: `${pct} % de ton billet`, pct,
      texte: r < 60 ? "Versé en bon d'achat, parce que ton retard fait moins d'1 h." : "Versé par virement, parce que ton retard dépasse 1 h.",
      forme: r < 60 ? "Bon d'achat" : "Virement", regle: "Garantie G30", lien: LIENS.g30,
      g30: "La garantie G30, c'est la compensation SNCF des TGV INOUI et Intercités dès 30 min de retard." };
  }
  if (t.regle === "ouigo") {
    if (r < 60) return { ton: "none", tampon: "Pas de droit", titre: "Pas de dédommagement",
      texte: "Moins d'1 h de retard à ta gare. OUIGO dédommage à partir d'1 h.", regle: "OUIGO", suite: SUITE_STANDARD };
    const pct = palier(r, [[60, 25], [120, 50]]);
    return { ton: "auto", tampon: "Automatique", titre: `${pct} % de ton billet`, pct,
      texte: "Rien à faire : OUIGO t'envoie un e-mail. Pas reçu sous 15 jours ? Contacte OUIGO.",
      forme: "Automatique", regle: "OUIGO", lien: LIENS.ouigo };
  }
  if (t.regle === "ter-krono") {
    if (r < 30) return { ton: "none", tampon: "Pas de droit", titre: "Pas de dédommagement",
      texte: "Moins de 30 min de retard à ta gare. Les trains Krono+ de Normandie dédommagent à partir de 30 min.", regle: "Krono+ Normandie", suite: SUITE_STANDARD };
    const pct = palier(r, [[30, 25], [120, 50], [180, 75]]);
    return { ton: "ok", tampon: "Droit ouvert", titre: `${pct} % de ton billet`, pct,
      texte: "Versé en bon voyage numérique. Fais ta demande sous 30 jours.", forme: "Bon voyage", regle: "Krono+ Normandie", lien: LIENS.krono };
  }
  return { ton: "none", tampon: "Pas de droit", titre: "Pas de remboursement par train",
    texte: `TER ${t.region} : la région ne dédommage pas un billet à l'unité, train par train.`,
    regle: `TER ${t.region}`, lien: LIENS.ter, suite: SUITE_STANDARD };
}

const retardMax = (t) => t.gares[t.gares.length - 1][1];
const route = (t) => `${t.gares[0][0]} → ${t.gares[t.gares.length - 1][0]}`;
const jourLabel = (d) => (d === AUJOURDHUI ? "aujourd'hui" : d === HIER ? "hier" : d);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const norm = (s) => (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const ICO_EXT = '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>';
// Libellé de lien externe : l'icône reste collée au dernier mot
function libelleExt(txt) {
  const m = String(txt).split(" "), fin = m.pop();
  return `<span>${esc(m.join(" "))} <span class="nw">${esc(fin)} ${ICO_EXT}</span></span>`;
}
