// Données réelles : API du site (backend/api.py). Les droits viennent du serveur (backend/regles.py) ;
// ce fichier ne fait que les mettre en forme pour le reçu.
"use strict";

const jourParis = (decalage = 0) => {
  const d = new Date(Date.now() + decalage * 86400000);
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Paris" }).format(d); // AAAA-MM-JJ
};
const AUJOURDHUI = jourParis(0);
const HIER = jourParis(-1);

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const norm = (s) => (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const ICO_EXT = '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>';
function libelleExt(txt) {
  const m = String(txt).split(" "), fin = m.pop();
  return `<span>${esc(m.join(" "))} <span class="nw">${esc(fin)} ${ICO_EXT}</span></span>`;
}
// Index du palier fixe : 0 = moins de 30, 1 = 30, 2 = 60, 3 = 120, 4 = 180 min et plus
const indexPalier = (r) => (r >= 180 ? 4 : r >= 120 ? 3 : r >= 60 ? 2 : r >= 30 ? 1 : 0);
const exemple = (pct) => `Sur un billet à 80 €, ça fait ${Math.round(80 * pct / 100)} €.`;
const jourLabel = (d) => {
  if (d === AUJOURDHUI) return "aujourd'hui";
  if (d === HIER) return "hier";
  const [a, m, j] = d.split("-");
  return `le ${j}/${m}/${a}`;
};
const retardMax = (t) => Math.max(0, ...t.gares.slice(1).map((g) => g[1] ?? 0));
const route = (t) => `${t.gares[0][0]} → ${t.gares[t.gares.length - 1][0]}`;

const SUITE_STANDARD = [
  { texte: "Tu avais une correspondance avec un billet unique ? C'est le retard à ta destination finale qui compte.",
    action: "Chercher mon dernier train" },
  { texte: "Abonné ? Ta région prévoit peut-être une compensation mensuelle.",
    action: "Voir les compensations TER", lien: "https://www.sncf-voyageurs.com/fr/contactez-nous/en-cas-de-retard/ter-transilien/" },
];

// Train de l'API → forme utilisée par la page :
// gares = [[nom, retard en min, droit], …] ; la première est la gare de départ.
// Les gares sans retard connu ou dont l'arrêt est supprimé ne sont pas proposées.
function versTrain(a) {
  const gares = a.gares.filter((g, i) => i === 0 || (g.retard_min !== null && !g.saute && g.droit))
    .map((g, i) => [g.nom, i === 0 ? 0 : Math.max(0, g.retard_min), g.droit]);
  return { date: a.jour, prod: a.nom, produit: a.produit, num: a.numero, h: a.depart || "—",
           cause: a.cause, supprime: a.supprime, droitSuppression: a.droit_suppression,
           majA: a.derniere_annonce, gares };
}

function lienDemande(d, t) {
  if (!d.lien) return null;
  if (t.produit === "OGO") return ["Contacter OUIGO", d.lien];
  if (["TER", "TER*", "TT", "NAV"].includes(t.produit)) return ["Voir la garantie de la région", d.lien];
  return ["Faire ma demande", d.lien];
}

// Droit du serveur → contenu du reçu.
function droit(t, d) {
  const ouvert = ["droit", "automatique", "remboursement"].includes(d.statut);
  const titre = d.statut === "remboursement" ? "Remboursement intégral"
    : d.pourcentage ? `${d.pourcentage} % de ton billet`
    : d.statut === "droit" || d.statut === "automatique" ? "Indemnisation possible"
    : d.statut === "cas_par_cas" ? "Réclamation possible" : "Pas de dédommagement";
  return {
    ton: !ouvert ? "none" : d.statut === "automatique" ? "auto" : "ok",
    tampon: d.statut === "automatique" ? "Automatique" : ouvert ? "Droit ouvert"
      : d.statut === "cas_par_cas" ? "Au cas par cas" : "Pas de droit",
    titre, texte: d.message, pct: d.statut === "remboursement" ? null : d.pourcentage,
    forme: d.forme, regle: d.regle_nom, lien: lienDemande(d, t), aConfirmer: d.a_confirmer,
    suite: t.supprime ? [{ texte: "Tu as pris un autre train ? Ton droit dépend alors de ton retard à l'arrivée.", action: "Chercher ce train" }]
      : !ouvert ? SUITE_STANDARD : null,
  };
}

async function api(chemin, params) {
  const r = await fetch(`${chemin}?${new URLSearchParams(params)}`, { cache: "no-store" });
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`API ${r.status}`);
  return r.json();
}
const trouverTrains = async (num, jour) => ((await api("/api/train", { numero: num, jour })) || { trains: [] }).trains.map(versTrain);
const chercherParGares = async (arrivee, depart) => (await api("/api/recherche", { arrivee, depart })).trains.map(versTrain);
