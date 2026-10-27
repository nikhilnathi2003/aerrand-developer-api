# Tracking & cancellation (Sai)

## Live tracking
`GET /v1/errands/{id}/tracking` returns status, the driver (name, vehicle, plate, rating), live
location, an **ETA**, and a timeline. In the sandbox `POST /v1/errands/{id}/advance` walks the
delivery through its stages and moves the driver pickup -> drop-off, so it can be shown without a
real driver. ETA is estimated in `apiv1/eta.py`.

## Cancellation rules (`apiv1/lifecycle.py`)
- You **can't cancel once the driver has picked up** (or it's delivered/cancelled) -> `409`.
- A **fee** applies once a driver has accepted/arrived; before that it's free.
- `POST /v1/errands/{id}/cancel` enforces this, refunds `paid - fee` to the wallet, and emits an
  `errand.cancelled` event.
