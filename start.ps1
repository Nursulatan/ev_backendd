$ErrorActionPreference = "Stop"
Write-Host "=== EV Backend (Auto-setup) ==="
Set-Location $PSScriptRoot
try { python --version | Out-Null } catch {
  Write-Host "Python not found. Installing via winget (admin prompt)..." -ForegroundColor Yellow
  Start-Process powershell -Verb RunAs -ArgumentList "winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements"
  Read-Host "Press Enter after installation completes"
}
if (-not (Test-Path "venv")) { Write-Host "Creating venv..."; python -m venv venv }
. "$PSScriptRoot\venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
python -m pip install -r "$PSScriptRoot\requirements.txt"
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env"; Write-Host ".env created." }
Write-Host "Starting server on http://127.0.0.1:10000 ..."
python -m uvicorn app.main:app --host 127.0.0.1 --port 10000 --reload --env-file .env

