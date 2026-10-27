# Evidence Trail — Aerrand Group 6

We've kept this log since week 1. It has a team log (what we planned vs what we
actually did each week) and a short log per person for our own parts. Weeks run
Monday to Sunday. "Evidence" points to a commit, the board, or the demo.

Milestones we set at the start: design done early Oct, core booking by ~Oct 19,
payments + safety by end of Oct, webhooks + test mode by mid Nov, final demo end of Nov.

---

## Team log

| Week | What we planned | What we actually did | Evidence | What changed | Next |
|------|-----------------|----------------------|----------|--------------|------|
| 1 (Sep 22–28) | Understand the project from the kickoff and set up the repo | Set up the GitHub repo and wrote the proposal, requirements and architecture notes | Repo + planning docs | — | Write the setup report, start building |
| 2 (Sep 29–Oct 5) | Finish the P1 setup report, get the backend running | Wrote the P1 report; set up the Django backend with MongoDB + Redis and a health check | P1 report; `/v1/health` works | Decided to use mock data and build to the payloads doc | Build the keys and pricing |
| 3 (Oct 6–12) | Office hours, finalise the plan | Went to office hours and settled the API design. No code this week | Updated plan; notes | Scopes are create / read / cancel | Start the core build |
| 4 (Oct 13–19) | Build the core: keys, pricing, booking | Built the API key system, pricing engine, quotes and create-delivery, and a developer dashboard | Commits Oct 16, 18, 19; demo | Scope grew — we added a proper dashboard | Wallet, tracking, webhooks |
| 5 (Oct 20–26) | Wallet, tracking, webhooks + a real UI | Added the wallet, live tracking, cancellation rules and signed webhooks; rebuilt the UI into a developer portal; added safe-retry booking. Everyone added their module | Commits from all four (Oct 25, 26); live demo | We're a bit ahead of plan | Rate limiting, more tests |
| 6 (Oct 27 – now) | Rate limiting, tidy up, prep the Week 7 eval | Added rate limiting; each of us added tests and a doc for our own area | Commits Oct 27; tests passing (90+) | — | Webhook delivery, API docs |

---

## Our own logs

### Nikhil — API keys, authentication, portal

| Week | What I did | Evidence | Done? |
|------|------------|----------|-------|
| 1 | Set up the repo and the planning docs | Commits | Yes |
| 2 | Wrote the P1 report and got the Django backend running | Commits / P1 | Yes |
| 4 | Built the API key system, auth and the developer console | Commits | Yes |
| 5 | Built the developer portal and wired wallet/tracking/webhooks into the API | Commits | Yes |
| 6 | Added rate limiting and safe-retry booking; went over the whole codebase | Commits | In progress |

### Sujith — pricing, booking, scheduling

| Week | What I did | Evidence | Done? |
|------|------------|----------|-------|
| 1–3 | Joined the meetings and went through the pricing/booking requirements | Meetings | Yes |
| 4 | Helped with the pricing and create-delivery work | Commits | Yes |
| 5 | Built the scheduled-delivery validation | Commit (`scheduling.py`) | Yes |
| 6 | Added pricing tests, a pricing doc and the vehicle-tier rule | Commits | In progress |

### Charan — wallet, webhooks

| Week | What I did | Evidence | Done? |
|------|------------|----------|-------|
| 1–3 | Joined the meetings and went through the wallet/webhook requirements | Meetings | Yes |
| 5 | Built the simple wallet (balance, charge, refund) | Commit (`wallet.py`) | Yes |
| 6 | Added wallet tests, a wallet/webhooks doc and the webhook verifier | Commits | In progress |

### Sai — tracking, cancellation

| Week | What I did | Evidence | Done? |
|------|------------|----------|-------|
| 1–3 | Joined the meetings and went through the tracking/cancellation requirements | Meetings | Yes |
| 5 | Built the lifecycle and cancellation rules | Commit (`lifecycle.py`) | Yes |
| 6 | Added tracking tests, a tracking doc and the ETA helper | Commits | In progress |

---

We update this every week: each person adds a line with a real evidence link, and we
move the matching card on the board to Done.
