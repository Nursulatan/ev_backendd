@echo off
setlocal
cd /d %~dp0
echo === EV Backend (Auto-setup) ===

where python >nul 2>&1
if %errorlevel% neq 0 (
  echo Python not found. Installing Python 3.11 via winget (admin prompt)...
  powershell -Command "Start-Process powershell -Verb RunAs -ArgumentList 'winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements'"
  echo When installation finishes, close and re-run this window if needed.
  pause
)

if not exist venv (
  echo Creating venv...
  python -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if not exist .env (
  copy .env.example .env >nul
  echo .env created.
)

echo Starting server on http://127.0.0.1:8000 ...
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
