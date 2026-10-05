# API Contract (v1) — what we build to

Source of truth for request/response shapes: `docs/source/aerrand-api-payloads.pdf`
(the sample data Johnpaul provided). This file is the quick reference.

> Naming note: the payloads doc uses `/v1/errands`, `errand_id`, and `ak_live_`/`ak_test_`
> keys. The earlier TRD used `/v1/aerrands` and `aer_live_`. **We follow the payloads doc**
> (errands / ak_ keys), since it's the concrete contract we were given to build against.

## Base + auth

- Base URL: `/v1`
- Header: `Authorization: Bearer ak_live_...` (or `ak_test_...`)
- `Content-Type: application/json`
- `Idempotency-Key: <uuid>` on create/cancel

## Endpoints

| Purpose | Method + path | Scope |
|---------|---------------|-------|
| Quote a price | `POST /v1/quotes` | read |
| Create a delivery | `POST /v1/errands` | write |
| Get a delivery | `GET /v1/errands/{id}` | read |
| Track a delivery | `GET /v1/errands/{id}/tracking` | read |
| Public tracking (no auth) | `GET /v1/errands/{id}/public` | — |
| Update drop-off instructions | `PUT /v1/errands/{id}/dropoff` | write |
| Update pickup instructions | `PUT /v1/errands/{id}/pickup` | write |
| AI item checklist | `POST /v1/checklists/generate` | write |
| Attach a checklist | `POST /v1/errands/{id}/checklist` | write |
| Attach tags | `POST /v1/errands/{id}/tags` | write |
| Cancel | `POST /v1/errands/{id}/cancel` | cancel |
| Service coverage | `GET /v1/service-areas` | read |

## Pricing (route quote → `POST /v1/quotes`)

Server computes the price; `POST /v1/errands` takes the `quote_id`, **never a price**.

Breakdown fields: `dropBaseTotal` (first stop + each extra stop), `distanceCharge`
(km beyond free allowance), `sizeAddOnTotal` (per-parcel size add-ons), `handlingTotal`
(parcels beyond included count, per stop), `volumeSurcharge` (flat, van-on-volume),
`routePrice` (pre-tax), `hstRate` 0.13, `hst`, `chargeTotal` (tax in), `amount_cents`.
Also: `recommendedVehicle`, `requiresCargoVehicle`, `totalCargoUnits`, `overVanCapacity`.

A quote returns `quote_id` + `expires_at`. Expired quote → `409 quote_expired`.

## Create (single vs multi-stop)

- Single: top-level `dropoff` object + optional `parcel`.
- Multi-stop: `dropoffs[]` array (1–5 stops); each stop = Location + `reference` + `parcels`.
- Multi-stop writes **N delivery records sharing one `batch_id`** (one Aerrander job).
  Each stop has its own `errand_id`, `delivery_code`, status, and price share.
- Response status starts at `pending_payment` (invisible to drivers until paid).

## Statuses

`pending_payment` → `pending` → `broadcasted` → `accepted` → `arrived` → `picked_up`
→ `in_transit` → `arrived_dropoff` → `delivered`. Terminal: `cancelled`.
(Treat unknown statuses as "in progress".)

## Webhook events

`errand.payment_confirmed`, `errand.accepted`, `errand.arrived_pickup`, `errand.in_transit`,
`errand.arrived_dropoff`, `errand.delivered` (with `proof_of_delivery`), `errand.cancelled`,
`errand.dropoff_updated`. Signed: `Aerrand-Signature: t=<unix>,v1=<hex hmac_sha256>` over
`t + "." + raw_body`. At-least-once; dedupe on `id`.

## Enums

- `vehicle_type`: scooter · motorcycle · car · van · truck
- parcel `size`: small · medium · large · xl (or a weight in lbs)
- checklist size tier: small · medium · large · xlarge
- dropoff `preference`: leave_at_door · meet_at_door · meet_at_curb
- pickup `preference`: pickup
- payment `method`: invoice · checkout_link
- currency: CAD

## Returned identifiers

- `errand_id` — UUID; used for all follow-up calls (track, update, cancel)
- `batch_id` — UUID; groups the stops of one route
- `delivery_id` — 24-char hex; the Aerrander app's record
- `delivery_code` — 6 chars; handover code (keep off any customer-facing page)
- `quote_id` — binds a price to a booking

## Errors

| HTTP | code | meaning |
|------|------|---------|
| 400 | `validation_failed` | `details` maps field → messages |
| 400 | `route_over_capacity` | route exceeds one cargo van; split it |
| 401 | `invalid_api_key` | |
| 404 | `errand_not_found` | |
| 409 | `quote_expired` | request a new quote |
| 409 | `edit_window_closed` | too late to change instructions |
| 409 | `cancel_not_allowed` | Aerrander at the stop, or already delivered |
| 412 | `business_not_approved` | account under review |
| 412 | `service_area_unavailable` | pickup/drop-off outside a served city |
| 429 | `rate_limited` | retry with backoff |

## Service area (demo)

Windsor — center `lat 42.3149, lng -83.0364`, `radiusKm 20`, active. (`GET /v1/service-areas`)
