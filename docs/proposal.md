# Approach Proposal — Aerrand Developer API (v1)

**Team:** Business 3, Group 6 · **Course:** COMP8967 · **Partner:** Aerrand Technologies Inc.
**Status:** Draft for review · **Date:** 2026-09-28

---

## 1. Our understanding of the problem

Aerrand connects buyers of secondhand items to vetted local drivers ("Aerranders") who
verify, pick up, and deliver the item so people never meet a stranger. It is live in
Windsor today. To grow into "the trust and logistics layer embedded inside marketplace
platforms," Aerrand needs partners (e.g. Kijiji, Shopify stores, 3PLs) to book deliveries
**from their own software** instead of clicking through Aerrand's dashboard by hand.

That handshake — a partner's system proving "I am Acme Co. and I'm allowed to book" —
happens through an **API key**. Building that key infrastructure and a clean public API
around it is our project.

**The core risk we must remove:** today the delivery price is sent from the browser and the
server trusts it. That is fine when Aerrand's own dashboard is the only caller; it is a
security hole the moment an outside program can call in. So the server must compute price
itself, and the public API must be a **separate, locked-down front door**
(`api.aerrand.com/v1`) that reuses Aerrand's existing pricing and dispatch logic but exposes
nothing else. *New entrance, not a new building.*

## 2. What "done" looks like (success criteria)

Aerrand's own bar for judging, which we adopt as our definition of done:

> An approved business can get a test key, read the docs, and create a working test
> delivery in **under 10 minutes**, entirely on their own.

Plus, on Aerrand's side:
- Prices can never be tampered with by the caller.
- Keys are never stored in plaintext, and a leaked key can be revoked instantly.
- **Zero impact** on the existing dashboard or driver experience.

## 3. Scope

**In scope (v1):**
- API key lifecycle: issuance, scoping, rotation, revocation, auditing.
- Public endpoints: quotes, aerrand creation (single & multi-stop), reads, tracking,
  cancellation, wallet balance, webhooks.
- Automated wallet payment (prepaid balance debit) + hosted-checkout fallback.
- Webhooks for every lifecycle event, including driver-side events.
- Safety rails: idempotency, rate limiting, strict tenant isolation.
- Developer documentation (OpenAPI spec + quickstart).

**Out of scope (v1), per the TRD:**
- Aerrand Guard (escrow / vendor KYC) via API.
- OAuth 2.0 / third-party platform apps (keys are per-business only).
- Postpaid invoicing / card-on-file (wallet or hosted Stripe Checkout only in v1).
- Replacing the dashboard's own booking flow.
- Customer-side (consumer app) developer access.

## 4. Key design decisions (and why)

| Decision | Our approach | Why |
|----------|-------------|-----|
| **Isolation** | New Django app `developer/`, new host `api.aerrand.com`, served only `/v1/*` + docs via Caddy | Keeps the public surface off the legacy `AllowAny` endpoints; no CORS/cookies/CSRF on the API origin |
| **Key storage** | Store only `HMAC-SHA256(pepper, key)` + a short display prefix; return the full key exactly once | A database leak alone can't verify keys; matches Stripe-style UX |
| **Pricing integrity** | Server recomputes price from `stops[].parcels` + routed km; client price is never read | Closes the "book at $0.50" hole (GAP-1) |
| **Payment** | Atomic wallet debit at creation (`F("balance") - total`) with `402` on shortfall; checkout mode kept for human-in-the-loop | Fully automated booking without a human clicking "pay" |
| **Cross-service events** | **Transactional outbox**: Django *and* the Node driver backend insert rows into a shared `webhook_outbox`; a background dispatcher signs & delivers them | Django can't observe the Node driver's status changes directly; polling is laggy and brittle — the outbox is explicit, testable, and adds no new infrastructure |
| **Reliability** | Idempotency keys, Redis-backed rate limits, per-request tenant scoping | These are table stakes for any real public API |

## 5. Proposed architecture (summary)

```
Integrator (ERP / storefront)
        │  Bearer aer_live_… key
        ▼
   Caddy (api.aerrand.com)  ──►  Django `developer/` app  ──►  MongoDB (shared)
        │                              │  reuses pricing + dispatch      ▲
        │                              └──────────────────────────┐     │ outbox rows
        ▼                                                         │     │
   Redis (rate limits, idempotency)              webhook_outbox ◄─┴─────┘
                                                        │
   Node driver backend ── outbox rows ──────────────────┘
                                                        │
                              webhook dispatcher (signs + POSTs, retries) ──► Integrator's URL
```

Full detail in [`architecture.md`](./architecture.md).

## 6. How we'll work

- **Backlog:** every requirement in the TRD has a stable ID (`FR-KEY-01`, …). We convert
  each into a GitHub issue (see [`requirements.md`](./requirements.md)) tagged with its
  MoSCoW priority and pillar. This is our source of truth.
- **Board:** a GitHub Project mirrors Aerrand's 4-phase rollout plan
  (see [`rollout-plan.md`](./rollout-plan.md)) so our columns match the client's own plan.
- **Process:** branch-per-issue, pull-request review by a teammate, `main` stays green.
  See [`CONTRIBUTING.md`](../CONTRIBUTING.md).

## 7. Open questions for Aerrand

Carried from §14 of the TRD; the ones that most affect our early work:

1. **Codebase access** — will the team get access to the `Aerrand_backen_infra` monorepo,
   or do we build a standalone implementation to spec? *(This is our #1 blocker.)*
2. **OQ-1:** confirm the channel value `"api"` (vs reusing `"business"`) for API aerrands.
3. **OQ-9:** will `STRIPE_SECRET_KEY_BUSINESS` move to a live key before GA?
4. **OQ-5:** should business pricing constants move to a DB-backed config so price changes
   don't require a deploy?
5. **Test data / pilot business** — can we get a sandbox business account + test wallet?

## 8. Risks

| Risk | Mitigation |
|------|-----------|
| We may not get the real codebase | Build to the spec's interfaces; keep our code liftable into the monorepo |
| The outbox spans two services (Django + Node) | Prototype the outbox + dispatcher early (Phase 2 in the plan); heavy test coverage |
| Pricing must match the dashboard "to the cent" | Adopt the TRD's parity test (`POST /v1/quotes == POST /order/business/route/estimate`) |
| Team is new to Django/Node/Mongo | Front-load Phase 0 foundations; pair on the first vertical slice |
