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

Données brutes dans `poc/data/` (gitignored), environ 200 Mo par jour.
