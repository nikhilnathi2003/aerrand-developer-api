# Architecture (our understanding of the target design)

This restates Aerrand's TRD §3–§7 in our own words, so the whole team shares one mental
model. Authoritative source: the TRD in `docs/source/`.

## 1. Current system (the baseline we must respect)

Aerrand runs a single-droplet Docker Compose stack:

- **`aerrand_api`** — Django, the main backend. Talks to MongoDB via `django-mongodb-backend`.
- **`aerrand_customer_backend`** / **`aerrand_driver_backend`** — Node services (mongoose).
  The **driver backend** owns the driver app's status changes.
- **`aerrand_business` / `aerrand_admin`** — React SPAs.
- **Caddy** — reverse proxy / TLS in front of everything.
- **MongoDB** — one shared database used by all backends.
- **No Redis today**, and Django uses per-process LocMemCache.

Key existing behaviours:
- Django `Order` rows are mirrored into a shared `deliveries` collection by
  `DeliveryService.sync_from_order`.
- **The price bug we're fixing:** for `business` orders the server trusts the client's price
  ("that client price already comes from an authoritative server endpoint, so we trust it").
- Driver-side transitions (accept / pickup / deliver) happen in the **Node** service, writing
  the Mongo delivery doc + RTDB directly. Django only learns about them when a client polls
  `/order/{id}/tracking`.
- Auth today = DRF **Token** (`Authorization: Token <40-hex>`), one token per user, stored in
  plaintext in Mongo, no scopes, no rotation. Not acceptable as developer credentials.

## 2. Target: a separate front door

We add a **new public host `api.aerrand.com`** and a **new Django app `developer/`**.

- Caddy on `api.aerrand.com` proxies **only** `/v1/*`, `/v1/openapi.json`, `/docs`, `/health`
  to `aerrand-api:8000`. Everything else on that host → `404`. Legacy routes
  (`/order/*`, `/custom-user/*`, `/admin/*`, `/swagger/*`) are **not reachable** here.
- `/v1/*` is not served on `app.` / `business.` / `admin.aerrand.com` → the API lives on a
  clean origin with no CORS, no cookies, no CSRF.
- The legacy `/order/*` flow is **untouched** — additive only.

## 3. Request pipeline (`/v1/*`)

1. Caddy terminates TLS, forwards `X-Forwarded-Proto`, injects `X-Request-Id` if absent.
2. `ApiKeyAuthentication` parses `Authorization: Bearer aer_(live|test)_…`, hashes it, looks
   up `api_keys.key_hash` (unique index), rejects revoked/expired, resolves
   `request.user = business owner`, `request.auth = ApiKey`.
3. `HasApiScope` checks the view's required scope against the key's scopes.
4. Business eligibility: `412` on non-approved (identical rule to the dashboard).
5. Redis throttles → `429` with `Retry-After`.
6. `@idempotent` (mutating endpoints only) replays a stored response or claims the key.
7. Service layer executes; **every DB read is scoped to `customer_id == owner.id`**.
8. Response: JSON, `X-Request-Id`, `X-RateLimit-*` headers; `ApiRequestLog` written async.

## 4. The outbox pattern (the hard part)

**Problem:** Django cannot observe the Node driver backend's writes to `deliveries`, so it
can't reliably emit `aerrand.accepted … delivered` webhooks. Polling is laggy and misses
transient states; Mongo change streams / RTDB listeners are brittle.

**Solution (chosen):** a **transactional outbox**. Both backends insert an event row into a
shared `webhook_outbox` collection at the exact points where they already do work:

- **Django** writes rows for the transitions it sees (`created`, `paid`, `searching`,
  `cancelled`) via `notify_order_status` → `webhooks.enqueue_from_order`.
- **Node driver backend** — a new `services/webhookOutbox.js`, called from
  `deliveryController.js` on accept/arrived/picked_up/in_transit/delivered/driver-cancel,
  guarded by `delivery.channel === 'api'` (or owner has ≥1 enabled endpoint).

A separate **dispatcher** container (`aerrand-webhook-dispatcher`, same image as `aerrand_api`
running `python manage.py run_webhook_dispatcher`) polls the outbox every ~2 s, claims rows
with a lease (`findOneAndUpdate`, 60 s expiry), builds the **public** Aerrand snapshot, signs
it (HMAC-SHA256), POSTs to the partner's URL, records `webhook_deliveries`, and schedules
retries. Writers never serialise the full object — keeping Node's change tiny and the public
shape defined in one place (Django).

## 5. Payment models

| Mode | v1? | Flow |
|------|-----|------|
| **wallet** (default) | Yes | Atomic debit at create; order paid immediately + broadcast to drivers. Refund-to-wallet on cancel minus policy fee. |
| **checkout** | Yes | Stripe Checkout (business key); aerrand stays `pending_payment` until the Stripe webhook. Auto-cancelled after `API_UNPAID_TTL_HOURS`. |
| card_on_file | Phase 2/4 | Stripe SetupIntent, off-session. |
| invoice | Phase 3 | Postpaid. |

## 6. New data model (all in the shared Mongo DB, Django-owned)

| Collection | Purpose |
|-----------|---------|
| `api_keys` | id, business_owner_id, name, environment, key_prefix, key_hash, scopes, status, expires_at, ip_allowlist, rate_limit_override, last_used_* , audit fields |
| `api_quotes` | quote_id, business_owner_id, api_key_id, inputs_hash, breakdown, total, expires_at (TTL) |
| `api_idempotency_keys` | (api_key_id, key) unique, fingerprint, status, response, TTL 24 h |
| `webhook_endpoints` | url, events, secret_encrypted (Fernet), previous_secret (rotation overlap), status, failure counters |
| `webhook_outbox` | event_type, order_id, batch_id, business_owner_id, channel, previous_status, status (pending/claimed/dispatched/dropped), lease fields, TTL 30 d |
| `webhook_deliveries` | endpoint_id, event_id, attempt, response_status, duration_ms, next_retry_at, status |
| `api_request_logs` | request_id, api_key_id, method, path, status, duration_ms, ip (no bodies/headers), TTL 7 d |
| `api_audit_log` | key/webhook/admin actions, actor, ip, user_agent, detail (no TTL) |

Changes to existing models are **additive + nullable**: `Order` gains `channel="api"`,
`api_key_id`, `external_reference`, `metadata`, `test_mode`, `payment_mode`; `Delivery` gains
an `origin` sub-doc; `WalletTransaction` gains `aerrand_charge`/`aerrand_refund` types.

## 7. Config & deployment (additive)

- New settings from the shared root `.env` (see TRD Appendix D). Two known pitfalls in this
  stack: inline `#` comments and trailing whitespace break `.env` values, and `docker compose
  watch` does not re-read `.env` — use `--force-recreate --build`.
- `API_KEY_HASH_PEPPER` and `WEBHOOK_SECRET_ENCRYPTION_KEY` are generated once and backed up
  (losing either invalidates all keys / all webhook secrets).
- New containers: `redis` and `aerrand-webhook-dispatcher`. Deploy order: Django (+migrations
  at container start) → Node (outbox writes harmless before dispatcher exists) → SPAs.
- Feature flags: `API_KEYS_ENABLED` (global), `BusinessProfile.api_access_enabled`
  (per-business), `API_WEBHOOKS_ENABLED`.

## 8. Non-functionals we're held to

- Latency: p95 ≤ 400 ms create (with quote), ≤ 150 ms reads.
- Webhook: event enqueued → first attempt ≤ 5 s p95; ≥ 99% delivery success.
- No new managed services besides Redis; everything in the existing compose + CI.
- Existing test suite must stay green; Node changes are insert-only, wrapped in try/catch,
  never block the transition.
