# Rollout Plan (mirrors Aerrand TRD §13)

We map Aerrand's own phased plan onto our GitHub Project board so our columns reflect the
client's plan. Each phase is a board **milestone/iteration**; issues carry their `FR-*` ID.

| Phase | Scope | Exit criteria |
|-------|-------|---------------|
| **0 — Foundations** (1–2 wks) | Redis + dispatcher service, Caddy host + DNS, `developer` app skeleton, `Order`/`Wallet`/`BusinessProfile` migrations, refactors in `order/views.py` (paid path, cancel path, Stripe key resolution), pepper/encryption keys provisioned | Existing suite green on staging; `GET /v1/health` monitored |
| **1 — Private beta** (2–3 wks) | Keys (create/revoke/rotate), quotes, `/v1/me`, create (wallet + checkout), get/list/tracking, cancel, idempotency, rate limits, dashboard Developers section (keys only), admin panel, docs | Acceptance items 1–4, 6 pass; `API_KEYS_ENABLED=true` on 2–3 pilot businesses only |
| **2 — Webhooks & test mode** (2 wks) | Outbox writers (Django + Node), dispatcher delivery/retries, endpoint management (API + dashboard), event history/redeliver, test-mode `advance`, Postman collection | Webhook success ≥ 99% over 1 wk; E2E item 2 |
| **3 — General availability** | `api_access_enabled` default on for all approved businesses; marketing page; SDKs (Could) | Support runbook written; on-call knows the kill switches |
| **4 — Payments expansion** | `card_on_file` (Stripe SetupIntent/off-session), auto-refill wallet, `wallet.balance_low`, Stripe reconciliation for checkout cancellations | Separate TRD |

## Suggested board columns

`Backlog` → `This Phase` → `In Progress` → `In Review` → `Done`

Use board **fields**:
- **Priority:** Must / Should / Could (from MoSCoW)
- **Pillar:** Keys / Auth / Pricing / Payment / Webhooks / Reads / Cancel / Safety / UI / Docs
- **Phase:** 0 / 1 / 2 / 3 / 4

## Rollback (from the TRD)

Set `API_KEYS_ENABLED=false` (all `/v1` → 503) and stop the dispatcher. No data migration
needs reversing — new fields are nullable and new collections are additive.
