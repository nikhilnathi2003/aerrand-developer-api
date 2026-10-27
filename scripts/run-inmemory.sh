#!/bin/bash
# Run the Aerrand API locally with NO MongoDB or Redis needed — just Python.
# Data lives in memory while the server runs (fine for trying the app / the demo).
# When it starts, open:  http://127.0.0.1:8000/
set -e
cd "$(dirname "$0")/../backend"

export DJANGO_SETTINGS_MODULE=config.settings
export API_KEY_HASH_PEPPER=dev-pepper-local
export INMEMORY_DB=1

if [ ! -d .venv ]; then
  echo "Creating Python environment (first run only)…"
  python3 -m venv .venv
  ./.venv/bin/pip install -q -r requirements.txt
fi

./.venv/bin/python manage.py migrate --noinput >/dev/null

echo ""
echo "  ➜  Open the portal:  http://127.0.0.1:8000/"
echo "     (Ctrl+C to stop)"
echo ""
exec ./.venv/bin/python manage.py runserver 127.0.0.1:8000
