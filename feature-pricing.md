# Pricing & scheduling (Sujith)

## Server-side pricing
A business never sends a price. `POST /v1/quotes` takes the pickup, the stops and their parcels,
and the server computes everything in `apiv1/pricing.py`:
- **dropBaseTotal** first stop + a charge per extra stop
- **distanceCharge** routed km (haversine x1.3 when there's no Google Distance Matrix key)
- **sizeAddOnTotal** per-parcel add-ons; **handlingTotal** parcels beyond the included count
- **volumeSurcharge** flat, when the load needs a van on volume alone
- **routePrice** (pre-tax) -> **hst** (13%) -> **chargeTotal** (tax in)

It also returns `recommendedVehicle`, `totalCargoUnits` and `overVanCapacity`. The quote returns a
`quote_id` that `POST /v1/errands` binds to, so the price is reused, never taken from the caller.

## Scheduled deliveries
`scheduled_at` is validated in `apiv1/scheduling.py`: no earlier than 5 min ago, no more than 7
days out. Empty means ASAP.

## Vehicle rule
A supplied vehicle must be at least the recommended tier (`apiv1/vehicles.py`).
