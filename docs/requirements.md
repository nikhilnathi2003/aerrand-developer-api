# Requirements Backlog (from Aerrand TRD §5)

Every requirement below has a **stable ID** from Aerrand's TRD and a **MoSCoW priority**
(M = Must, S = Should, C = Could). This file is the source of truth for our GitHub issues:
each row becomes one issue, labelled with its priority and pillar.

> Tip: when creating issues, title them `FR-KEY-01: A key is owned by a business owner account`
> and label `priority:must` + `pillar:keys` + `phase:0`.

Legend for pillars → board field: **Keys, Auth, Elig, Pricing (Quotes+Create), Payment,
Reads, Cancel, Webhooks, Safety (Idem+Rate), Test, UI, Docs.**

---

## 5.1 API key lifecycle — pillar: Keys

| ID | Pri | Requirement |
|----|-----|-------------|
| FR-KEY-01 | M | A key is owned by a **business owner account** (not an individual member). |
| FR-KEY-02 | M | Only the owner + `business_admin` role may create/rotate/revoke; other roles may only list (prefix only). |
| FR-KEY-03 | M | Keys can be created only when the business is **approved**; non-approved businesses see the Developers section disabled. |
| FR-KEY-04 | M | Key format `aer_<env>_<40 chars base62>`, entropy ≥ 230 bits (`secrets.token_bytes(32)`). |
| FR-KEY-05 | M | Full key returned **exactly once**; persist only `key_prefix` + `key_hash = HMAC-SHA256(pepper, key)`. Never store plaintext. |
| FR-KEY-06 | M | Attributes at creation: `name` (1–64 chars, unique per business), `environment`, `scopes`, default `expires_at` ≤ 1 year. |
| FR-KEY-07 | M | Revoke is immediate + irreversible; revoked key → `401 api_key_revoked`. |
| FR-KEY-08 | S | Rotate: new key, same name/scopes/env; old key gets 24 h grace (0–72 h configurable) then auto-revoked. |
| FR-KEY-09 | M | Limit ≤ 10 active keys per environment per business (admin override). |
| FR-KEY-10 | M | `last_used_at` / `last_used_ip` updated at most once per 60 s per key (write-coalesced). |
| FR-KEY-11 | M | Every create/rotate/revoke writes an audit row + emails the owner. |
| FR-KEY-12 | S | Global kill switch `API_KEYS_ENABLED=false` → all `/v1` return `503`. Per-business switch too. |
| FR-KEY-13 | C | Owner-initiated "revoke all keys" panic button in the dashboard. |

## 5.2 Authentication & authorization — pillar: Auth

| ID | Pri | Requirement |
|----|-----|-------------|
| FR-AUTH-01 | M | Header `Authorization: Bearer <key>` (or `X-Api-Key` alias). Query-string keys rejected `400 api_key_in_query`. |
| FR-AUTH-02 | M | `ApiKeyAuthentication` attached only to `/v1` views; DRF Token auth not accepted on `/v1`, API keys not accepted on legacy routes. |
| FR-AUTH-03 | M | Scopes: `quotes:read`, `aerrands:read`, `aerrands:write`, `aerrands:cancel`, `webhooks:manage`. Missing scope → `403 insufficient_scope`. |
| FR-AUTH-04 | M | Environment binding: a `test` key can only touch `test_mode=true` aerrands and vice versa; cross-env reads → `404`. |
| FR-AUTH-05 | M | IP allowlist (when set) enforced against `X-Forwarded-For`; mismatch → `403 ip_not_allowed`. |
| FR-AUTH-06 | M | Failed-auth responses are uniform (`401 invalid_api_key`) and constant-time w.r.t. prefix. |
| FR-AUTH-07 | M | All `/v1` responses include `Cache-Control: no-store`. |

## 5.3 Business eligibility — pillar: Elig

| ID | Pri | Requirement |
|----|-----|-------------|
| FR-ELIG-01 | M | Every mutating `/v1` request re-evaluates business approval; rejected/suspended → `412 business_not_approved`. Reads still allowed. |
| FR-ELIG-02 | M | Approval status changes don't touch keys, but a rejection blocks creation from the next request onward. |
| FR-ELIG-03 | S | `GET /v1/me` exposes approval status, `can_create_aerrands`, `api_access_enabled`, wallet summary. |

## 5.4 Quotes — pillar: Pricing

| ID | Pri | Requirement |
|----|-----|-------------|
| FR-QUOTE-01 | M | `POST /v1/quotes` accepts pickup + 1..5 stops with parcels, returns full breakdown + recommended vehicle + route km + total (HST-inclusive) — same numbers as the dashboard estimate. |
| FR-QUOTE-02 | M | Route km = sum of sequential legs via Google Distance Matrix (haversine ×1.3 fallback). Priced in given order. |
| FR-QUOTE-03 | M | Each quote persisted with `quote_id = qt_<uuid>`, inputs hash, breakdown, `expires_at = now + API_QUOTE_TTL_SECONDS` (default 600). |
| FR-QUOTE-04 | M | Validation: >5 stops `400 too_many_stops`; >20 cargo units `400 over_van_capacity`; no parcels on a stop `400 stop_without_parcels`; out of service area `400 outside_service_area`. |
| FR-QUOTE-05 | S | Optional address strings: when `lat/lng` omitted + `address` present, geocode with Google; failures → `422 address_not_found`. |

## 5.5 Aerrand creation — pillar: Pricing

| ID | Pri | Requirement |
|----|-----|-------------|
| FR-CREATE-01 | M | `POST /v1/aerrands` creates a single- or multi-stop (≤5) aerrand in one call. |
| FR-CREATE-02 | M | Creation is **atomic** across stops (all rows exist and are paid/pending together, or none) via `transaction.atomic()` (+ compensation on the replica set). |
| FR-CREATE-03 | M | Each stop → one `Order` row; N>1 rows share a `batch_id` + `batch_index`; N=1 keeps batch fields `null`. |
| FR-CREATE-04 | M | Price computed server-side: reuse stored quote if `quote_id` supplied + unexpired + inputs hash matches; else re-price. Client never sends price. Optional `max_total` → `409 price_exceeds_max`. |
| FR-CREATE-05 | M | Per-stop `Order.price` = equal split of `chargeTotal`, cents reconciled on last stop; `delivery_fee`, `price_breakdown` populated. |
| FR-CREATE-06 | M | `Order.size` = lbs-equivalent of largest parcel class on the stop; `Order.volume` = total parcel count. |
| FR-CREATE-07 | M | `vehicle` optional (default recommended); a supplied vehicle must be ≥ recommended tier else `400 vehicle_below_requirement`. |
| FR-CREATE-08 | M | `scheduled_at` (ISO-8601, optional): must be ≥ now−5min and ≤ now+7 days; absent = ASAP. |
| FR-CREATE-09 | M | Server sets `channel="api"`, `api_key_id`, `external_reference` (≤128 chars, unique per business per env → `409 duplicate_external_reference` unless allowed), `test_mode`, `payment_mode`. Metadata ≤20 keys. |
| FR-CREATE-10 | M | Pickup contact defaults to business profile when omitted; recipient `name` + `phone` required per stop (E.164). `dropoff_preference` maps to internal preference. |
| FR-CREATE-11 | M | After rows exist, `DeliveryService.sync_from_order` runs per row (test-mode syncs as pending; paid syncs as broadcasted). |
| FR-CREATE-12 | M | Response is `201` with the full public Aerrand object; checkout mode adds `payment.checkout_url`. |
| FR-CREATE-13 | M | Guard/escrow inputs (`declared_item_value`, `order_type="aerrand_guard"`) rejected `400 unsupported_order_type`. |
| FR-CREATE-14 | S | In-app notification + RTDB push to owner on creation so the dashboard live feed shows API aerrands without a refresh. |

## 5.6 Payment — pillar: Payment

| ID | Pri | Requirement |
|----|-----|-------------|
| FR-PAY-01 | M | `payment.mode` in `{wallet, checkout}`; default `wallet`. |
| FR-PAY-02 | M | Wallet debit is atomic + race-safe (`balance__gte=total` conditional update); 0 rows → `402 insufficient_funds` with `{required, available, currency, topup_url}`. Decimal, quantised to cents. |
| FR-PAY-03 | M | Successful debit writes a `WalletTransaction(type=aerrand_charge, amount=-total, order_id, …)`. New txn types `aerrand_charge` + `aerrand_refund`. |
| FR-PAY-04 | M | After debit, each row goes through the existing paid path (refactored `mark_order_paid`), status `pending → broadcasted`, outbox `aerrand.paid`. |
| FR-PAY-05 | M | Wallet mode in `test` performs no debit + no txn; response still reports `payment.status="paid"` with `reference="test"`. |
| FR-PAY-06 | M | Checkout mode creates a Stripe payment link with the **business** Stripe key resolved from the key owner (never from Origin — closes GAP-2). |
| FR-PAY-07 | M | Unpaid checkout aerrands auto-cancelled (no fee) after `API_UNPAID_TTL_HOURS` (default 24); emit `aerrand.cancelled` with `reason=payment_expired`. |
| FR-PAY-08 | M | Prereq flagged: `STRIPE_SECRET_KEY_BUSINESS` is currently a test key; live checkout needs it switched + matching webhook secret. |
| FR-PAY-09 | S | `GET /v1/wallet` returns balance, currency, pending topups, last 20 transactions, `topup_url`. |
| FR-PAY-10 | C | Low-balance webhook `wallet.balance_low` when balance drops below a business threshold. |

## 5.7 Reads, listing & tracking — pillar: Reads

| ID | Pri | Requirement |
|----|-----|-------------|
| FR-READ-01 | M | `GET /v1/aerrands/{id}` resolves batch id or order id (scoped to owner); live fields merged from the deliveries doc. |
| FR-READ-02 | M | `GET /v1/aerrands` supports filters (status, external_reference, created/scheduled ranges, limit ≤100) + opaque cursor pagination, sorted `created_at desc`. |
| FR-READ-03 | M | `GET /v1/aerrands/{id}/tracking` returns lightweight live view (status, driver, location, ETA, per-stop timeline) + token-less `tracking_url`. |
| FR-READ-04 | S | `GET /v1/aerrands/{id}/proof` returns delivery photos/handoff data for delivered stops as short-lived signed URLs. |
| FR-READ-05 | M | `GET /v1/events` lists last 30 days of webhook events for the business (for reconciliation), filterable, cursor-paginated. |

## 5.8 Cancellation — pillar: Cancel

| ID | Pri | Requirement |
|----|-----|-------------|
| FR-CANCEL-01 | M | `POST /v1/aerrands/{id}/cancel` (scope `aerrands:cancel`) cancels all non-terminal stops using the existing fee engine per row. |
| FR-CANCEL-02 | M | If any stop can't be cancelled → `409 cancellation_not_allowed` with per-stop reasons, nothing cancelled (all-or-nothing) unless `partial=true`. |
| FR-CANCEL-03 | M | Wallet-paid: refund = `paid_total − Σ fee` credited atomically; response includes fee, refund, aerrander compensation, from_stage. |
| FR-CANCEL-04 | M | Emits `aerrand.cancelled` with reason in `{business_request, payment_expired, driver_no_show, admin}` + fee outcome. |
| FR-CANCEL-05 | C | `PATCH /v1/aerrands/{id}` for pre-dispatch edits (instructions, recipient phone); address/parcel changes require cancel + recreate in v1. |

## 5.9 Webhooks — pillar: Webhooks

| ID | Pri | Requirement |
|----|-----|-------------|
| FR-WH-01 | M | Register ≤5 endpoints (`POST /v1/webhooks` or dashboard): url (https, ≤2048), events (list or `["*"]`), description. Signing secret returned once (`aer_whsec_<40 base62>`). |
| FR-WH-02 | M | Secret stored encrypted at rest (Fernet). Never returned after creation; `rotate-secret` issues a new one with 24 h overlap (both secrets sign during overlap). |
| FR-WH-03 | M | Event catalogue: `aerrand.created/paid/searching/accepted/arrived_at_pickup/picked_up/in_transit/stop_delivered/delivered/cancelled/payment_expired`, `wallet.balance_low`. |
| FR-WH-04 | M | Envelope `{id, type, api_version, created, test_mode, data:{object, previous_status}}`; snapshot built at dispatch time. |
| FR-WH-05 | M | Signature header `Aerrand-Signature: t=<unix>,v1=<HMAC-SHA256(secret, "<t>.<raw body>")>`; receivers must reject stale timestamps. |
| FR-WH-06 | M | At-least-once, ordered per aerrand best-effort; receivers dedupe by `id`; success = any `2xx` within `WEBHOOK_TIMEOUT_SECONDS` (10). No redirects. |
| FR-WH-07 | M | Retry schedule 1m/5m/30m/2h/12h/24h (6 attempts); after 6 days of failures, endpoint auto-disabled + owner emailed. |
| FR-WH-08 | M | SSRF protection: resolve hostname, refuse loopback/RFC1918/link-local/CGNAT/multicast/metadata ranges; refuse non-443/80 unless allowed; refuse `.local/.internal`. |
| FR-WH-09 | M | `POST /v1/webhooks/{id}/test` sends synthetic `aerrand.created` (test_mode); `POST /v1/events/{id}/redeliver` re-enqueues. Delivery attempts visible. |
| FR-WH-10 | M | Outbox writers (Django + Node) insert `{event_type, order_id, batch_id, business_owner_id, channel, previous_status, created_at, status:"pending"}`; the dispatcher builds the payload (Node never serialises the full object). |
| FR-WH-11 | M | Events enqueued only for `channel="api"` orders or where the owner has ≥1 enabled endpoint. |

## 5.10 Idempotency — pillar: Safety

| ID | Pri | Requirement |
|----|-----|-------------|
| FR-IDEM-01 | M | `POST /v1/aerrands`, `/cancel`, `/webhooks` accept `Idempotency-Key` (1–255 chars); required for create in `live` (else `400 idempotency_key_required`). |
| FR-IDEM-02 | M | Scope = (api_key_id, key). First request claims (`in_progress`, unique index), stores fingerprint = SHA-256(method+path+canonical body). Completion stores response. TTL 24 h. |
| FR-IDEM-03 | M | Replay same fingerprint → stored response + `Idempotent-Replayed: true`. Same key, different fingerprint → `422 idempotency_key_reused`. Concurrent → `409 idempotency_in_progress`. |
| FR-IDEM-04 | M | If the original request failed 5xx, the claim is released so the client can retry. |

## 5.11 Rate limiting & quotas — pillar: Safety

| ID | Pri | Requirement |
|----|-----|-------------|
| FR-RATE-01 | M | Per-key sliding-window limits (default 60/min, 3000/hr all endpoints; `POST /v1/aerrands` 20/min; `POST /v1/quotes` 120/min; test keys ×2). |
| FR-RATE-02 | M | Storage Redis; if `REDIS_URL` unset, fall back to LocMemCache with a startup warning (dev only). |
| FR-RATE-03 | M | Headers on every response: `X-RateLimit-Limit/Remaining/Reset`. Exceeded → `429 rate_limited` + `Retry-After`. |
| FR-RATE-04 | S | Daily creation quota (default 2000/day) → `429 daily_quota_exceeded`. |
| FR-RATE-05 | M | Unauthenticated / failed-auth requests limited per IP (30/min). |

## 5.12 Test mode — pillar: Test

| ID | Pri | Requirement |
|----|-----|-------------|
| FR-TEST-01 | M | `aer_test_` keys create `test_mode=True` aerrands: never synced to deliveries, never debit wallet, no Stripe, no RTDB, excluded from admin aggregates/reports. |
| FR-TEST-02 | M | Test aerrands visible in the business dashboard only behind a "Show test data" toggle (TEST badge). |
| FR-TEST-03 | S | `POST /v1/test/aerrands/{id}/advance {to}` walks a test aerrand forward through valid transitions + emits webhooks (no driver needed). |
| FR-TEST-04 | S | Test data older than 30 days purged by a management command. |

## 5.13 Business dashboard UI — pillar: UI

| ID | Pri | Requirement |
|----|-----|-------------|
| FR-UI-01 | M | New Profile → "Developers" section (icon Code), visible to all roles, actionable per FR-KEY-02. |
| FR-UI-02 | M | Keys table: name, prefix, env chip, scopes, created, last used, status; Rotate/Revoke actions (confirm dialog names the key). |
| FR-UI-03 | M | "Create key" modal: name, environment, scope checkboxes (all on by default), optional expiry; success shows full key once with copy + "You won't see this again". |
| FR-UI-04 | M | Webhooks tab: endpoint list (url, events, status, last delivery), add/edit/disable, "send test event", secret shown once, delivery log with status/latency + "Redeliver". |
| FR-UI-05 | S | Logs tab: last 7 days of API requests (time, method, path, status, latency, request id). |
| FR-UI-06 | M | Links to `https://api.aerrand.com/docs` + the quickstart. |
| FR-UI-07 | M | Aerrands lists widened to `channel=business,api` + "API" badge; DeliveryDetail shows `external_reference` + metadata. |
| FR-UI-08 | M | Dashboard endpoints (Token-auth, `IsAuthenticated`) for keys/webhooks/logs; enforce role per FR-KEY-02. |

## 5.14 Admin dashboard — pillar: UI

| ID | Pri | Requirement |
|----|-----|-------------|
| FR-ADMIN-01 | M | BusinessesPage gains an "API access" panel: `api_access_enabled` toggle, keys list, admin Revoke, rate-limit + daily-quota overrides. |
| FR-ADMIN-02 | M | Admin endpoints follow the existing `_require_admin` pattern. |
| FR-ADMIN-03 | S | Admin "API overview" card: requests/24h, aerrands via API/24h, webhook failure rate, top businesses. |
| FR-ADMIN-04 | S | Orders/Deliveries page filter by `channel=api` + show `external_reference`. |

## 5.15 Developer documentation — pillar: Docs

| ID | Pri | Requirement |
|----|-----|-------------|
| FR-DOCS-01 | M | Hand-maintained OpenAPI 3.1 spec at `api.aerrand.com/v1/openapi.json`, Redoc at `/docs`. |
| FR-DOCS-02 | M | Quickstart (create key → quote → create → webhook), auth/idempotency/rate-limit samples (Node, Python, PHP), error catalogue, status lifecycle, changelog. |
| FR-DOCS-03 | S | Postman collection generated from the v1 spec. |
| FR-DOCS-04 | C | Minimal official SDKs (TypeScript, Python) generated from the spec. |

---

## Counts (for planning)

- **Must (M):** the backbone — do these first (Phases 0–2).
- **Should (S):** valuable, schedule into the same phase where cheap.
- **Could (C):** stretch / Phase 3–4.

See [`rollout-plan.md`](./rollout-plan.md) for which phase each pillar lands in.
