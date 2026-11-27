#!/bin/bash
# Run the Aerrand API locally with NO MongoDB or Redis needed — just Python.
# Data lives in memory while the server runs (fine for trying the app / the demo).
# When it starts, open:  http://127.0.0.1:8000/
set -e
cd "$(dirname "$0")/../backend"

export DJANGO_SETTINGS_MODULE=config.settings
export API_KEY_HASH_PEPPER=dev-pepper-local
export INMEMORY_DB=1

# Optional: load Gmail credentials for real low-balance emails (git-ignored, private).
# Create backend/.env.email with EMAIL_HOST_USER and EMAIL_HOST_PASSWORD to enable.
if [ -f .env.email ]; then
  while IFS='=' read -r _k _v || [ -n "$_k" ]; do
    case "$_k" in ''|\#*) continue;; esac
    _v="${_v// /}"       # App Passwords are shown with spaces — strip them
    _v="${_v%$'\r'}"     # strip trailing CR if the file was edited on Windows
    export "$_k=$_v"
  done < .env.email
  echo "  ✉  Real emails ON — sending from: $EMAIL_HOST_USER"
else
  echo "  ✉  Email: log-only (no backend/.env.email found)"
fi

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
