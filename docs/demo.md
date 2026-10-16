# Monday demo — key → quote → priced test-mode errand

This is the Milestone 2 flow: a valid **test API key** creates a correctly-priced
**test-mode errand**, live.

## Easiest: local, no Docker (already set up on this Mac)

Two terminals, from the repo root:

```bash
# Terminal 1 — start the API (MongoDB + Redis + Django)
./scripts/start-local.sh
```
```bash
# Terminal 2 — run the whole demo (issue key → quote → create → get → safety)
./scripts/demo.sh
```

`start-local.sh` starts MongoDB + Redis (Homebrew services), sets up the Python env, and
runs the server at http://127.0.0.1:8000. `demo.sh` runs the full flow and prints each step.
Run the tests any time with: `cd backend && ./.venv/bin/python manage.py test`.

The manual Docker walkthrough below is the alternative (for teammates who use Docker).

---

## Docker alternative

## 0. Start the stack

```bash
docker compose up --build
```

Wait until it's up, then check: open http://localhost:8000/v1/health
→ `{"status":"ok", "mongodb":"connected", "redis":"connected"}`

## 1. Issue a test API key (keys are issued by command, not a dashboard)

In a second terminal:

```bash
docker compose exec api python manage.py issue_key --business "Acme Co" --env test
```

Copy the `ak_test_…` it prints (shown once). For the commands below:

```bash
export KEY=ak_test_PASTE_IT_HERE
```

## 2. Get a quote (server computes the price)

```bash
curl -s http://localhost:8000/v1/quotes \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"pickup":{"lat":"42.3149","lng":"-83.0364"},
       "stops":[{"lat":"42.3201","lng":"-83.0187","parcels":{"small":2,"medium":1}}]}'
```

You get a `quote_id` and the full breakdown (`dropBaseTotal`, `distanceCharge`,
`chargeTotal`, `recommendedVehicle`, …). Copy the quote id:

```bash
export QUOTE=qt_PASTE_IT_HERE
```

## 3. Create the errand (price comes from the quote, never the caller)

```bash
curl -s http://localhost:8000/v1/errands \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d "{\"quote_id\":\"$QUOTE\",
       \"pickup\":{\"lat\":\"42.3149\",\"lng\":\"-83.0364\"},
       \"dropoff\":{\"lat\":\"42.3201\",\"lng\":\"-83.0187\",
                    \"contact\":{\"name\":\"Jordan\",\"phone_number\":\"+15195550188\"},
                    \"preference\":\"leave_at_door\"}}"
```

You get back an `errand_id`, a `delivery_code`, `test_mode: true`, and the pricing.
Copy the errand id:

```bash
export ERRAND=PASTE_errand_id_HERE
```

## 4. Fetch it back

```bash
curl -s http://localhost:8000/v1/errands/$ERRAND -H "Authorization: Bearer $KEY"
```

## 5. (Optional) show the safety rails

- **Server-trusted price:** there's no way to send a price — it only takes `quote_id`.
- **Tenant isolation:** issue a key for another business and try to GET the same errand → `404`.
- **Scopes:** a read-only key (`--scopes read`) trying to create → `403 insufficient_scope`.
- **Revocation:** `docker compose exec api python manage.py revoke_key --prefix <prefix>` → that key now returns `401`.

## 6. Run the tests (shows it's verified)

```bash
docker compose exec api python manage.py test
```

---

Note: distance uses a haversine ×1.3 estimate (we don't have Google's Distance Matrix
key), so `routeKm` and the distance charge are close to — not identical to — Aerrand's.
The pricing *structure* and all other numbers match their contract.
