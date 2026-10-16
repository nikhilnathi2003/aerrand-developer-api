#!/bin/bash
# One-command demo: issue a key, get a quote, create a test-mode errand, fetch it.
# Run this in a second terminal while ./scripts/start-local.sh is running.
set -e
cd "$(dirname "$0")/../backend"
export MONGO_URL=mongodb://localhost:27017/aerrand REDIS_URL=redis://localhost:6379/0 \
       API_KEY_HASH_PEPPER=dev-pepper-local DJANGO_SETTINGS_MODULE=config.settings
BASE=http://127.0.0.1:8000

curl -s $BASE/v1/health >/dev/null 2>&1 || { echo "Start the server first:  ./scripts/start-local.sh"; exit 1; }

line() { echo; echo "────────────────────────────────────────"; echo "$1"; echo "────────────────────────────────────────"; }

line "1) Issue a test API key (by command)"
KEY=$(./.venv/bin/python manage.py issue_key --business "Acme Co" --env test | grep -o 'ak_test_[A-Za-z0-9]*')
echo "   $KEY"

line "2) POST /v1/quotes  (server computes the price)"
Q=$(curl -s $BASE/v1/quotes -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"pickup":{"lat":"42.3149","lng":"-83.0364"},"stops":[{"lat":"42.3201","lng":"-83.0187","parcels":{"small":2,"medium":1}}]}')
echo "$Q" | python3 -m json.tool
QID=$(echo "$Q" | python3 -c "import sys,json;print(json.load(sys.stdin)['quote_id'])")

line "3) POST /v1/errands  (priced from the quote, test-mode)"
R=$(curl -s $BASE/v1/errands -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d "{\"quote_id\":\"$QID\",\"pickup\":{\"lat\":\"42.3149\",\"lng\":\"-83.0364\"},\"dropoff\":{\"lat\":\"42.3201\",\"lng\":\"-83.0187\",\"contact\":{\"name\":\"Jordan Alvarez\",\"phone_number\":\"+15195550188\"},\"preference\":\"leave_at_door\"}}")
echo "$R" | python3 -m json.tool
EID=$(echo "$R" | python3 -c "import sys,json;print(json.load(sys.stdin)['errand_id'])")

line "4) GET /v1/errands/$EID"
curl -s $BASE/v1/errands/$EID -H "Authorization: Bearer $KEY" | python3 -m json.tool

line "5) Safety rails"
echo -n "   no API key        -> HTTP "; curl -s -o /dev/null -w "%{http_code}\n" $BASE/v1/errands/$EID
echo -n "   create w/o quote   -> HTTP "; curl -s -o /dev/null -w "%{http_code}\n" $BASE/v1/errands -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -d '{"price":"0.50"}'
echo
echo "Done. (Price comes only from a server quote; a leaked/revoked key → 401; one business can't read another's errand.)"
