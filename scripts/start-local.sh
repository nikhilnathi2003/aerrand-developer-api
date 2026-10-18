#!/bin/bash
# Start the API locally (no Docker): MongoDB + Redis + Django on http://127.0.0.1:8000
set -e
cd "$(dirname "$0")/../backend"

export MONGO_URL=mongodb://localhost:27017/aerrand
export REDIS_URL=redis://localhost:6379/0
export API_KEY_HASH_PEPPER=dev-pepper-local
export DJANGO_SETTINGS_MODULE=config.settings

echo "Starting MongoDB + Redis…"
brew services start redis >/dev/null 2>&1 || true
brew services start mongodb/brew/mongodb-community >/dev/null 2>&1 || true

if [ ! -d .venv ]; then
  echo "Creating Python environment…"
  python3.13 -m venv .venv
  ./.venv/bin/pip install -q -r requirements.txt
fi

./.venv/bin/python manage.py migrate --noinput >/dev/null

echo ""
echo "  ➜  Open the dashboard:  http://127.0.0.1:8000/"
echo "     (API health check:   http://127.0.0.1:8000/v1/health)"
echo "     Ctrl+C to stop."
echo ""
exec ./.venv/bin/python manage.py runserver 127.0.0.1:8000
