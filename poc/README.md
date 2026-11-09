# POC — flux temps réel SNCF (jalon 1)

Prototype jetable : vérifier que le GTFS-RT SNCF permet de détecter de façon fiable les trains
ouvrant droit à remboursement. Conclusions à reporter dans `PROJECT.md`.

```bash
venv/Scripts/python -m pip install -r poc/requirements.txt
venv/Scripts/python poc/collect.py --once   # un relevé de test
venv/Scripts/python poc/collect.py          # collecte continue (toutes les 2 min)
venv/Scripts/python poc/analyse.py          # rapport par jour → poc/data/rapport_<jour>.md
```

Collecte détachée (Windows, PowerShell) :
```powershell
Start-Process venv\Scripts\python.exe poc\collect.py -WindowStyle Hidden -PassThru   # démarrer
Stop-Process -Id (Get-Content poc\data\collect.pid)                                  # arrêter
```

## Sur le VPS (depuis le 2026-11-09)

La collecte tourne sur le VPS de rertracker, dans son propre projet Docker (`~/monretard/`),
sans rien partager avec rertracker. Elle redémarre seule (`restart: unless-stopped`).

```bash
# déployer / mettre à jour (depuis poc/)
tar cf - Dockerfile docker-compose.yml .dockerignore collect.py analyse.py regions.py requirements.txt \
  | ssh ubuntu@149.56.102.94 "mkdir -p ~/monretard/data && tar xf - -C ~/monretard && cd ~/monretard && docker compose up -d --build"
ssh ubuntu@149.56.102.94 "cd ~/monretard && docker compose logs --tail 20"          # suivre
ssh ubuntu@149.56.102.94 "cd ~/monretard && docker compose exec collecte python analyse.py"   # rapports dans data/
```

Données brutes dans `data/` (gitignored). Mesuré sur PC : ~200 Mo par jour complet, dont plus de la
moitié en Service Alerts — désormais stockées seulement quand elles changent. Fichiers bruts et GTFS
effacés au-delà de 7 jours (`--garder-jours`), journal plafonné (3 × 5 Mo).
