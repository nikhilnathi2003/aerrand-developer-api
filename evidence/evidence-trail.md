# Evidence Trail — Aerrand Group-6

Project log kept from week 1: a **team log** plus a small **individual contribution log** per
member. Weeks run Monday–Sunday. "Evidence" links to a commit, the board, or a demo.

Milestones: M1 Oct 4 (design) · M2 Oct 18 (core booking) · M3 Nov 1 (payments & safety) ·
M4 Nov 15 (webhooks & test mode) · M5 Nov 30 (integration & demo).

---

## Team log

| Week | What we planned | What we built | Evidence | What changed | Next step |
|------|-----------------|---------------|----------|--------------|-----------|
| 1 (Sep 21–27) | Kickoff; understand the project | — (understanding) | Kickoff attended; overview + TRD received | – | Set up repo + plan |
| 2 (Sep 28–Oct 4) | Set up project; plan; setup report | GitHub repo, project board, 102 issues, P1 report | Repo + board; `docs/P1-initial-setup-report.md` | – | Office hours; start building |
| 3 (Oct 5–11) | Office hours; start Sprint 1 | Backend scaffold (Django + MongoDB + Redis); `/v1/health` | Commits; `docker compose up` | Scope set: mock data, build to `/v1/errands` | API keys |
| 4 (Oct 12–18) | Core booking (M2): keys, pricing, create | API key system (hashed, scopes, revoke); server-side pricing engine; create delivery; developer console | Commits | Confirmed scopes = create/read/cancel per brief | Wallet, tracking |
| 5 (Oct 19–25) | Wallet, tracking, cancel, webhooks + a real UI | Prepaid wallet (charge/refund/statement); live driver tracking (map + ETA); cancel-with-fee rules; signed webhooks; full developer **portal**; each teammate's module | Commits from all 4; live demo | Scope grew into a full portal; well ahead of M2 | Safety rails |
| 6 (Oct 26–Nov 1) *(current)* | Safety rails (M3): idempotency, rate limiting; polish; Week-7 eval | Idempotency (replay-safe booking); UI polish; audit (36 tests, 17 edge cases); teammate tests + docs; rate limiting (in progress) | Commits from all 4; audit output | — | Webhook dispatcher (M4) |
| 7 (Nov 2–8) | Webhook dispatcher + retries | _(to update)_ | | | Test-mode advance |
| 8 (Nov 9–15) | Webhooks & test mode (M4) | _(to update)_ | | | Docs |
| 9 (Nov 16–22) | OpenAPI docs; hardening | _(to update)_ | | | Dry run |
| 10 (Nov 23–30) | Integration & final demo (M5) | _(to update)_ | | | Final demo |

---

## Individual contribution logs

### Nikhil Goud Nathi (lead · API keys + auth + integration)

| Week | My task | Evidence | Result | Next task |
|------|---------|----------|--------|-----------|
| 1 | Ask API-key questions at kickoff | Kickoff | Clarified scope | Set up repo |
| 2 | Set up repo, board, 102 issues; draft setup report | Commits / board / P1 | Done | Scaffold backend |
| 3 | Backend scaffold + `/v1/health` | Commits | Done | Key system |
| 4 | Build the API key system (hash, scopes, revoke, rotation, audit) + auth + console | Commits | Done | Wallet/tracking |
| 5 | Build the developer portal; wire wallet, tracking, webhooks into the API | Commits | Done | Safety rails |
| 6 | Add idempotency; polish the portal; audit the whole codebase | Commits; 36 tests | In progress | Webhook dispatcher |

### Sujith Chitram (pricing · booking · scheduling)

| Week | My task | Evidence | Result | Next task |
|------|---------|----------|--------|-----------|
| 1–3 | Attend meetings; review pricing/booking requirements | Meetings | Done | Plan quotes |
| 5 | Build the scheduled-delivery validation module | Commit (`scheduling.py`) | Done | Pricing tests |
| 6 | Add pricing unit tests, a pricing & scheduling doc, and the vehicle-tier rule | Commits | In progress | Quote parity tests |

### Venkata Charan Sai Doniparthi (wallet · webhooks)

| Week | My task | Evidence | Result | Next task |
|------|---------|----------|--------|-----------|
| 1–3 | Attend meetings; review wallet/webhook requirements | Meetings | Done | Plan wallet |
| 5 | Build the simple wallet module (balance, atomic debit, refund) | Commit (`wallet.py`) | Done | Wallet tests |
| 6 | Add wallet-statement tests, a wallet & webhooks doc, and the webhook signature verifier | Commits | In progress | Wire top-up to Stripe (phase 2) |

### Sai Srinivas Uppara (tracking · cancellation)

| Week | My task | Evidence | Result | Next task |
|------|---------|----------|--------|-----------|
| 1–3 | Attend meetings; review tracking/cancellation requirements | Meetings | Done | Plan tracking |
| 5 | Build the lifecycle + cancellation-rules module | Commit (`lifecycle.py`) | Done | Lifecycle tests |
| 6 | Add lifecycle tests, a tracking & cancellation doc, and the ETA helper | Commits | In progress | Proof-of-delivery endpoint |

---

### How we keep this current
Each week every person adds a row with a real Evidence link, and we move the matching issues on
the project board to Done.
