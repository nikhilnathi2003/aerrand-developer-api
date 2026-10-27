@echo off
REM Run the Aerrand API locally with NO MongoDB or Redis needed - just Python.
REM Data lives in memory while the server runs (fine for trying the app / the demo).
REM When it starts, open:  http://127.0.0.1:8000/
cd /d "%~dp0\..\backend"

set DJANGO_SETTINGS_MODULE=config.settings
set API_KEY_HASH_PEPPER=dev-pepper-local
set INMEMORY_DB=1

if not exist .venv (
  echo Creating Python environment (first run only)...
  python -m venv .venv
  .venv\Scripts\pip install -q -r requirements.txt
)

.venv\Scripts\python manage.py migrate --noinput

echo.
echo   Open the portal:  http://127.0.0.1:8000/
echo   (Ctrl+C to stop)
echo.
.venv\Scripts\python manage.py runserver 127.0.0.1:8000
