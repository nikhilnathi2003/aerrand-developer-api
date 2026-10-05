# Evidence Trail — Aerrand Group-6

Project log kept from week 1. Follows the course template: a **team log** plus a small
**individual contribution log** per member. Weeks run Monday–Sunday.
"Evidence" links to a commit, the board, or a demo.

> Weeks 1–3 record work already done (each member: confirm/adjust your own rows to match
> exactly what you did). Weeks 4–10 are the **planned** schedule by role, aligned to the
> course milestones — fill in real Evidence/Result as you complete each one.

Milestones: M1 Oct 4 (design) · M2 Oct 18 (core booking) · M3 Nov 1 (payments & safety) ·
M4 Nov 15 (webhooks & test mode) · M5 Nov 30 (integration & demo).

---

## Team log

| Week | What we planned | What we built | Evidence | What changed | Next step |
|------|-----------------|---------------|----------|--------------|-----------|
| 1 (Sep 21–27) | Attend kickoff; understand the project | — (understanding) | Kickoff attended; overview + TRD received | – | Set up repo + plan |
| 2 (Sep 28–Oct 4) | Set up project; plan; write setup report | GitHub repo, project board, 102 issues, P1 setup report | Repo + board; `docs/P1-initial-setup-report.md` | – | Office hours; start building |
| 3 (Oct 5–11) | Office hours; start Sprint 1 (scaffold + API keys) | Backend scaffold (Django + Docker + MongoDB + Redis); `/v1/health` | Commits; `docker compose up` → `/v1/health` ok | Scope clarified; build to `/v1/errands`; scopes = create/read/cancel | API key issuance + hashing |
| 4 (Oct 12–18) | Core booking (M2): key auth end-to-end; quote + create | _(to update)_ | _(commits/demo)_ | _(to update)_ | Wallet payment |
| 5 (Oct 19–25) | Stabilise booking; add tests | _(to update)_ | | | Safety rails |
| 6 (Oct 26–Nov 1) | Payments & safety rails (M3): wallet, cancel, idempotency, rate limit, tenant isolation | _(to update)_ | | | Webhooks |
| 7 (Nov 2–8) | Harden safety rails; tests | _(to update)_ | | | Outbox design |
| 8 (Nov 9–15) | Webhooks & test mode (M4): outbox + dispatcher, signed events | _(to update)_ | | | Reliability |
| 9 (Nov 16–22) | Webhook retries/reliability; simulate-delivery | _(to update)_ | | | Dashboard + docs |
| 10 (Nov 23–30) | Integration & demo (M5): dashboard, docs, live dry run | _(to update)_ | | | Final demo |

---

## Individual contribution logs

### Nikhil Goud Nathi (lead · API keys + auth)

| Week | My task | Evidence | Result | Next task |
|------|---------|----------|--------|-----------|
| 1 | Ask API-key questions at kickoff | Kickoff | Clarified scope | Set up repo |
| 2 | Set up repo, board, 102 issues; draft setup report + architecture | Commits / board / P1 report | Done | Scaffold backend |
| 3 | Backend scaffold + `/v1/health`; start API key system | Commits (`docker-compose`, `/v1/health`) | Scaffold runs | Key issuance + hashing |
| 4 | API key auth end-to-end (verify each request, scopes) | _(to update)_ | | Rate limiting |
| 5 | Review/tests for key + auth | _(to update)_ | | Tenant isolation |
| 6 | Tenant isolation + Redis rate limiting | _(to update)_ | | Webhook mgmt |
| 7 | Harden auth; failed-auth limits | _(to update)_ | | Webhook endpoints |
| 8 | Webhook management endpoints | _(to update)_ | | Dashboard keys |
| 9 | Key kill-switch / rotation polish | _(to update)_ | | Dashboard |
| 10 | Developers dashboard (create/revoke keys) | _(to update)_ | | Demo |

### Sujith Chitram (quotes · booking)

| Week | My task | Evidence | Result | Next task |
|------|---------|----------|--------|-----------|
| 1 | Attend kickoff; note pricing/booking requirements | Kickoff | Noted | Review quote flow |
| 2 | Review quote/create requirements; draft pricing section of report | P1 report | Done | Plan quote endpoint |
| 3 | Office hours (pricing + sample data); review API contract pricing | Notes / `docs/api-contract.md` | In progress | Build `POST /v1/quotes` |
| 4 | Build quote + create-delivery (correctly priced, test-mode) | _(to update)_ | | Multi-stop |
| 5 | Multi-stop create; validation errors | _(to update)_ | | Idempotency |
| 6 | Idempotency on create | _(to update)_ | | Tests |
| 7 | Pricing parity tests | _(to update)_ | | Simulate endpoint |
| 8 | Simulate-delivery endpoint for test keys | _(to update)_ | | Reliability |
| 9 | Booking edge cases + tests | _(to update)_ | | Dry run |
| 10 | Full live-mode dry run (<10 min demo) | _(to update)_ | | Demo |

### Venkata Charan Sai Doniparthi (wallet · webhooks)

| Week | My task | Evidence | Result | Next task |
|------|---------|----------|--------|-----------|
| 1 | Attend kickoff; note wallet/payment requirements | Kickoff | Noted | Review wallet flow |
| 2 | Review wallet/webhook requirements; draft payment section of report | P1 report | Done | Plan wallet |
| 3 | Office hours (wallet + webhooks); review wallet/webhook contract | Notes / `docs/api-contract.md` | In progress | Build simple wallet |
| 4 | Start wallet payment mode (charge on booking) | _(to update)_ | | Insufficient-funds |
| 5 | Insufficient-funds handling; refund path | _(to update)_ | | Tests |
| 6 | Wallet debit/refund complete + tests | _(to update)_ | | Outbox design |
| 7 | Design the outbox (Django + Node writers) | _(to update)_ | | Dispatcher |
| 8 | Outbox + dispatcher, signed events | _(to update)_ | | Retries |
| 9 | Webhook retries/reliability | _(to update)_ | | Webhook UI |
| 10 | Webhook management UI | _(to update)_ | | Demo |

### Sai Srinivas Uppara (tracking · cancellation · test mode · docs)

| Week | My task | Evidence | Result | Next task |
|------|---------|----------|--------|-----------|
| 1 | Attend kickoff; note tracking/cancellation requirements | Kickoff | Noted | Review tracking flow |
| 2 | Review tracking/cancel/docs requirements; draft sprint plan section | P1 report | Done | Plan tracking |
| 3 | Office hours (tracking + cancellation); review tracking/cancel contract | Notes / `docs/api-contract.md` | In progress | Build tracking |
| 4 | Build get + tracking endpoints | _(to update)_ | | Cancel |
| 5 | Public tracking endpoint | _(to update)_ | | Cancel rules |
| 6 | Cancel endpoint + fee rules | _(to update)_ | | Test mode |
| 7 | Test-mode behaviour (no driver, no charge) | _(to update)_ | | Event checks |
| 8 | Verify full signed event sequence (test mode) | _(to update)_ | | Docs |
| 9 | Draft developer documentation | _(to update)_ | | Publish docs |
| 10 | Publish public API docs | _(to update)_ | | Demo |

---

### How to update (every week)
1. Add/complete one row in the **team log**.
2. Each person completes their row in their **individual log** with a real Evidence link.
3. Move the matching issues on the project board to Done.
