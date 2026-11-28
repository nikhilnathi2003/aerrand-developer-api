# Aerrand Developer API — Business 3, Group 6

**Course:** COMP8967 — Master of Applied Computing, Industry Partnership Program (University of Windsor)
**Industry partner:** Aerrand Technologies Inc. (Windsor, ON)
**Team:** Business 3 — Group 6

> A secure, key-authenticated public API (`/v1`) that lets outside businesses quote, book,
> pay for, track, and cancel Aerrand deliveries programmatically — and receive webhooks —
> without ever touching Aerrand's existing dashboard or driver systems.

---

## Status

**Complete — final demo build.** The whole delivery loop works on test data: generate an
API key, get a server-computed price, book a delivery, pay from a prepaid wallet, track the
driver live, and receive signed webhooks. A developer portal ties it all together, and all
123 automated tests pass.

Working endpoints (all under `/v1/`):

- **Keys:** `POST /keys`, `POST /keys/revoke`, `POST /keys/rotate`, `GET /keys/audit`
- **Pricing & booking:** `POST /quotes`, `POST /errands` (single + multi-stop), `GET /errands/{id}`, `GET /geocode`, `GET /service-areas`
- **Wallet:** `GET /wallet`, `POST /wallet/topup`, `GET /wallet/statement.csv`
- **Tracking & cancel:** `GET /errands/{id}/tracking`, `POST /errands/{id}/cancel`, `GET /errands/{id}/proof`, `GET /livefeed`
- **Webhooks:** `GET /webhooks`, `POST /webhooks/test`, `GET /events`, `GET /webhooks/deliveries`
- **Health:** `GET /health`

Every request authenticates with `Authorization: Bearer ak_test_...`; keys are stored only
as a hash.

## Running the project (just Python — easiest)

No Docker, MongoDB, or Redis needed. You only need **Python 3.11+** installed. From the repo root:

**Mac / Linux:**
```bash
bash scripts/run-inmemory.sh
```

**Windows:** double-click `scripts\run-inmemory.bat` (or run it from a terminal).

The first run sets up the environment automatically. When it says it's ready, open:

- **http://127.0.0.1:8000/** — the developer portal

It uses an in-memory database, so data lasts while the server is running (perfect for
trying it out and for the demo). Stop it with `Ctrl+C`.

## Running the project (Docker, with persistent storage)

MongoDB support is built in; the Python-only mode above just runs in memory. To keep data
between restarts, run it with Docker (needs **Docker Desktop**). From the repo root:

```bash
docker compose up --build
```

This starts the Django API, MongoDB, and Redis. Once it's up, open:

- http://localhost:8000/v1/health

You should see `{"status": "ok", ..., "mongodb": "connected", "redis": "connected"}`.

Stop it with `Ctrl+C` (or `docker compose down`).

## Testing

Run the automated test suite from the `backend` folder:

```bash
cd backend
python manage.py test
```

All 123 tests should pass. To test the running app by hand in about a minute:

1. Open http://127.0.0.1:8000/ and go to **Create delivery**.
2. Click **Generate test key** — a key starting with `ak_test_` appears and the wallet shows a test balance.
3. Enter a Windsor pickup and drop-off and click **Get quote** — a price breakdown appears.
4. Click **Create delivery** — the wallet is charged and the delivery opens in live tracking.
5. Open **Webhooks** — signed events (created, paid, picked up) appear in the feed.

You can also check the API directly: `curl http://127.0.0.1:8000/v1/health`.

## What's in here

```
aerrand-developer-api/
├── README.md               ← you are here
├── CONTRIBUTING.md         ← how our team works (branches, commits, reviews)
├── docker-compose.yml      ← runs the API + MongoDB + Redis
├── scripts/                ← run-inmemory.sh / .bat (easiest way to run)
├── backend/                ← the Django API service
│   ├── config/             ← Django project (settings, urls)
│   ├── apiv1/              ← the full /v1 API (keys, pricing, wallet, tracking, webhooks)
│   └── requirements.txt
├── docs/                   ← api contract, proposal, requirements, architecture, demo
└── .gitignore
```

## The problem in one sentence

Today an outside business that wants Aerrand to deliver something has to log into Aerrand's
dashboard and fill in a form by hand. We built the API key + endpoints that let their
software do it automatically — priced by the server (never the client), authenticated by a
hashed API key, and safe to expose to the public internet.

## The five pillars

1. **API key issuance & authentication** — generate, hash-store, scope, and revoke keys.
2. **Server-trusted pricing & booking** — the server computes the price; never trust the client.
3. **Automated wallet payment** — atomic debit from the business's prepaid balance.
4. **Webhooks** — push signed lifecycle events so partners are notified automatically.
5. **Safety rails** — idempotency, rate limiting, and strict tenant isolation.

## Team

| Name | GitHub | Area |
|------|--------|------|
| Nikhil Goud Nathi | @nikhilnathi2003 | API keys & authentication, developer portal, rate limiting |
| Sujith Chitram | _add handle_ | Pricing, booking, saved addresses, coverage check |
| Venkata Charan Sai Doniparthi | @charansai50 | Prepaid wallet & signed webhooks |
| Sai Srinivas Uppara | @lucky100704 | Live tracking, proof of delivery, cancellation rules |

**Mentor (GA):** Rustem Izmailov

## Configuration note

The settings are for local development (`DEBUG=True`, console email, in-memory or local
MongoDB). Before any real deployment, set `DEBUG=False`, replace `SECRET_KEY` and
`API_KEY_HASH_PEPPER`, set a real `MONGO_URL`, and serve over HTTPS. Secrets stay in
environment variables, never in the code (see `.env.example`).
