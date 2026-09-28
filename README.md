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

**Proposal / approach phase.** This repository currently holds planning and design
documents only. No application code is written yet. The first deliverable is our
**approach proposal** (`docs/proposal.md`).

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
├── docs/
│   ├── proposal.md         ← our approach / pitch (first deliverable)
│   ├── requirements.md     ← Aerrand's TRD turned into a MoSCoW backlog (→ GitHub issues)
│   ├── architecture.md     ← the design in our own words
│   ├── rollout-plan.md     ← Aerrand's 4-phase plan mapped to our board
│   └── github-setup.md     ← how this org/repo/board is set up and how to add people
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
