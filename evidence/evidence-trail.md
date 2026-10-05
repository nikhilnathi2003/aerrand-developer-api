# Evidence Trail — Aerrand Group-6

Project log, kept from week 1. Format follows the course template:
a **team log** plus a small **individual contribution log** per member.
Weeks run Monday–Sunday. "Evidence" links to commits, the board, or a demo.

---

## Team log

| Week | What we planned | What we built | Evidence | What changed | Next step |
|------|-----------------|---------------|----------|--------------|-----------|
| 1 (Sep 21–27) | Attend kickoff; understand the project | — (understanding, no build yet) | Kickoff attended; received overview + TRD | – | Set up repo + plan |
| 2 (Sep 28–Oct 4) | Set up project; plan; write setup report | GitHub repo, project board, 102 issues, P1 setup report | Repo + board links; `docs/P1-initial-setup-report.md` | – | Office hours; start building |
| 3 (Oct 5–11) | Office hours; start Sprint 1 (backend scaffold + API keys) | Backend scaffold (Django + Docker + MongoDB + Redis); `/v1/health` working | Git commits; `docker compose up` → `/v1/health` returns ok | Scope clarified at office hours (mock data, simple wallet, keys issued by command); build to `/v1/errands` per sample data; scopes = create/read/cancel per brief | Build the API key system (issue, hash, verify, revoke) |

---

## Individual contribution logs

### Nikhil Goud Nathi (lead · API keys)

| Week | My task | Evidence | Result | Next task |
|------|---------|----------|--------|-----------|
| 1 | Ask API-key questions at kickoff | Kickoff meeting | Clarified scope | Set up repo |
| 2 | Set up repo, board, issues; draft setup report | Commits / board / P1 report | Done | Scaffold the backend |
| 3 | Backend scaffold + `/v1/health`; start API key system | Commits (`docker-compose`, `/v1/health`) | Scaffold runs | Build key issuance + hashing |

### Sujith Chitram (quotes · booking)

| Week | My task | Evidence | Result | Next task |
|------|---------|----------|--------|-----------|
| 1 | Attend kickoff; note the business challenge | Kickoff meeting | _(add)_ | _(add)_ |
| 2 | _(add your task)_ | _(add)_ | _(add)_ | _(add)_ |
| 3 | Review pricing/booking in the API contract; start quote endpoint | _(add commit)_ | _(in progress)_ | Build `POST /v1/quotes` |

### Venkata Charan Sai Doniparthi (wallet · webhooks)

| Week | My task | Evidence | Result | Next task |
|------|---------|----------|--------|-----------|
| 1 | Attend kickoff; take notes | Kickoff meeting | _(add)_ | _(add)_ |
| 2 | _(add your task)_ | _(add)_ | _(add)_ | _(add)_ |
| 3 | Review wallet/webhook requirements | _(add)_ | _(in progress)_ | Plan the simple wallet |

### Sai Srinivas Uppara (tracking · cancellation · docs)

| Week | My task | Evidence | Result | Next task |
|------|---------|----------|--------|-----------|
| 1 | Attend kickoff; take notes | Kickoff meeting | _(add)_ | _(add)_ |
| 2 | _(add your task)_ | _(add)_ | _(add)_ | _(add)_ |
| 3 | Review tracking/cancellation in the contract | _(add)_ | _(in progress)_ | Plan tracking + cancel rules |

---

### How to update (every week)
1. Add one row to the **team log**.
2. Each person adds one row to their **individual log**.
3. Put a real link in "Evidence" — a commit, the board, or a demo.
