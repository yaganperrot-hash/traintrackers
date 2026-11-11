# Site en local sur le PC : PostgreSQL + ingestion des relevés de poc/data + API et pages.
#   Lancer  : powershell -ExecutionPolicy Bypass -File deploy\local.ps1
#   Arrêter : powershell -ExecutionPolicy Bypass -File deploy\local.ps1 -Stop
# Puis http://127.0.0.1:8000
# Prérequis : .env à la racine (DATABASE_URL, ignoré par git) et PostgreSQL 16 dans
# %LOCALAPPDATA%\monretard (binaires pg16\, données pgdata\ — hors OneDrive). Voir README.
param([switch]$Stop)
$ErrorActionPreference = "Stop"
$racine = Split-Path $PSScriptRoot -Parent
$D = Join-Path $env:LOCALAPPDATA "monretard"
$pgctl = Join-Path $D "pg16\bin\pg_ctl.exe"
$pgdata = Join-Path $D "pgdata"
$python = Join-Path $racine "venv\Scripts\python.exe"
$port = 8000

function Arreter($nom) {
    $f = Join-Path $D "$nom.pid"
    if (Test-Path $f) {
        $p = Get-Process -Id (Get-Content $f) -ErrorAction SilentlyContinue
        if ($p -and $p.ProcessName -like "python*") { Stop-Process -Id $p.Id -Force }
        Remove-Item $f -Confirm:$false
    }
}

function Lancer($nom, $arguments) {
    Arreter $nom
    $p = Start-Process $python -ArgumentList $arguments -WorkingDirectory $racine -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $D "$nom.out.log") -RedirectStandardError (Join-Path $D "$nom.log")
    $p.Id | Out-File -Encoding ascii (Join-Path $D "$nom.pid")
}

function BaseDemarree { Test-Path (Join-Path $pgdata "postmaster.pid") }

# Pas de « Start-Process -Wait » : il attendrait aussi le serveur PostgreSQL lancé par pg_ctl, donc sans fin.
function PgCtl($arguments) {
    $p = Start-Process $pgctl -ArgumentList $arguments -WindowStyle Hidden -PassThru
    $p.WaitForExit()
}

if ($Stop) {
    Arreter "api"; Arreter "ingestion"
    if (BaseDemarree) { PgCtl "-D `"$pgdata`" -m fast -w stop" }
    "Site local arrêté."
    exit 0
}

# Variables du .env (jamais affichées)
Get-Content (Join-Path $racine ".env") | Where-Object { $_ -match '^\s*[^#].*=' } | ForEach-Object {
    $k, $v = $_ -split '=', 2
    [Environment]::SetEnvironmentVariable($k.Trim(), $v.Trim(), "Process")
}

if (-not (BaseDemarree)) {
    PgCtl "-D `"$pgdata`" -l `"$D\postgres.log`" -w start"
}
Lancer "ingestion" "-m backend.ingestion"
Lancer "api" "-m uvicorn backend.api:app --host 127.0.0.1 --port $port"
"Site local : http://127.0.0.1:$port   (journaux : $D)"
