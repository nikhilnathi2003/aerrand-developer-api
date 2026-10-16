# Aerrand Developer API — Business 3, Group 6

**Course:** COMP8967 — Master of Applied Computing, Industry Partnership Program (University of Windsor)
**Industry partner:** Aerrand Technologies Inc. (Windsor, ON)
**Team:** Business 3 — Group 6

> Building the "USB port" for secondhand marketplaces: a secure, key-authenticated
> public API (`api.aerrand.com/v1`) that lets outside businesses quote, book, pay for,
> track, and cancel Aerrand deliveries programmatically — and receive webhooks — without
> ever touching Aerrand's existing dashboard or driver systems.

---

## Current phase

**Building — Milestone 2 (core booking) works.** A test API key can get a priced quote
and create a correctly-priced **test-mode errand**, with tenant isolation and scopes.
See **`docs/demo.md`** for the live walkthrough.

Working endpoints: `POST /v1/quotes`, `POST /v1/errands` (single + multi-stop),
`GET /v1/errands/{id}`, `GET /v1/service-areas`, `GET /v1/health`.
Keys are issued by command (`python manage.py issue_key …`), stored only as a hash.
Next: wallet payment, tracking, cancel, then webhooks.

## Running the project (Docker)

You need **Docker Desktop** installed (free: https://www.docker.com/products/docker-desktop).
Then, from the repo root:

```bash
docker compose up --build
```

This starts three containers — the Django API, MongoDB, and Redis. Once it's up, open:

- http://localhost:8000/v1/health

You should see `{"status": "ok", ..., "mongodb": "connected", "redis": "connected"}`.

Stop it with `Ctrl+C` (or `docker compose down`).

## Links

| Thing | Link |
|-------|------|
| GitHub repo | _this repository_ |
| Project board (PM tool) | _add link once the org Project is created_ |
| Source documents from Aerrand | `docs/source/` (project overview + TRD) |

## What's in here

```
aerrand-developer-api/
├── README.md               ← you are here
├── CONTRIBUTING.md         ← how our team works (branches, commits, reviews)
├── docker-compose.yml      ← runs the API + MongoDB + Redis
├── backend/                ← the Django API service
│   ├── config/             ← Django project (settings, urls)
│   ├── apiv1/              ← the /v1 API app (health check for now)
│   ├── requirements.txt
│   └── Dockerfile
├── docs/
│   ├── api-contract.md     ← the v1 request/response shapes we build to
│   ├── P1-initial-setup-report.md
│   ├── proposal.md · requirements.md · architecture.md · rollout-plan.md
│   └── source/             ← original Aerrand PDFs (overview, TRD, API payloads)
├── evidence/
│   └── weekly-log.md       ← weekly progress & contribution log
└── .gitignore
```

## The problem in one sentence

Today an outside business that wants Aerrand to deliver something has to log into
Aerrand's dashboard and fill in a form by hand. We are building the API key + endpoints
that let their software do it automatically — priced by the server (never the client),
authenticated by a hashed API key, and safe to expose to the public internet.

## The five pillars

1. **API key issuance & authentication** — generate, hash-store, scope, and revoke keys.
2. **Server-trusted pricing & booking** — the server computes price; never trust the client.
3. **Automated wallet payment** — atomic debit from the business's prepaid balance.
4. **Webhooks via a transactional outbox** — push lifecycle events reliably across services.
5. **Safety rails** — idempotency, rate limiting, and strict tenant isolation.

## Team

| Name | GitHub | Role |
|------|--------|------|
| Nikhil Nathi | @nikhilnathi2003 | _tbd_ |
| _teammate_ | _@handle_ | _tbd_ |
| _teammate_ | _@handle_ | _tbd_ |
| _teammate_ | _@handle_ | _tbd_ |

**Mentor (GA):** Rustem Izmailov — _add GitHub handle when known_

_Fill this table in as usernames come in; see `docs/github-setup.md` for how to add people._
