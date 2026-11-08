"""Serveur local de travail pour les maquettes, avec rechargement automatique.

Lancement : venv/Scripts/python docs/maquettes/serveur.py   puis ouvrir http://127.0.0.1:8000
N'écoute que sur 127.0.0.1 (pas accessible depuis le réseau). Bibliothèque standard uniquement.
Quand un fichier du dossier change, les pages ouvertes se rechargent seules.
"""
import http.server
import os
import sys
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

SCRIPT = b"""<script>(function(){let v=null;setInterval(async()=>{try{const r=await fetch('/__version',{cache:'no-store'});
const t=await r.text();if(v!==null&&t!==v)location.reload();v=t;}catch(e){}},700);})();</script>"""


def version():
    return str(max(p.stat().st_mtime_ns for p in DOSSIER.iterdir() if p.is_file()))


class Gestionnaire(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(DOSSIER), **k)

    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def envoyer(self, corps, type_):
        self.send_response(200)
        self.send_header("Content-Type", type_)
        self.send_header("Content-Length", str(len(corps)))
        self.end_headers()
        self.wfile.write(corps)

    def do_GET(self):
        chemin = self.path.split("?", 1)[0].split("#", 1)[0]
        if chemin == "/__version":
            return self.envoyer(version().encode(), "text/plain; charset=utf-8")
        if chemin == "/":
            self.send_response(302)
            self.send_header("Location", "/site.html")
            return self.end_headers()
        if chemin.endswith(".html"):
            fichier = (DOSSIER / chemin.lstrip("/")).resolve()
            if fichier.parent == DOSSIER and fichier.is_file():
                corps = fichier.read_bytes().replace(b"</body>", SCRIPT + b"</body>", 1)
                return self.envoyer(corps, "text/html; charset=utf-8")
        return super().do_GET()


if __name__ == "__main__":
    os.chdir(DOSSIER)
    with http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Gestionnaire) as s:
        print(f"Maquettes sur http://127.0.0.1:{PORT}  (Ctrl+C pour arrêter)")
        s.serve_forever()
