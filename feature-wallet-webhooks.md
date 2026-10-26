# Wallet & webhooks (Charan)

## Prepaid wallet (`apiv1/wallet.py`)
- **debit** is atomic and race-safe: balance is checked in the same update, so two bookings can
  never overdraw it. Short funds -> `402`.
- **refund** credits the wallet on cancellation.
- Every movement (topup / charge / refund) is recorded in a **transaction statement** returned by
  `GET /v1/wallet`.

## Webhooks (`apiv1/webhooks.py`)
On every lifecycle change we record a **signed** event:
`Aerrand-Signature: t=<unix>,v1=<hex hmac_sha256(secret, "<t>.<body>")>`.
Partners verify it with `apiv1/webhook_verify.py`. Register endpoints with `POST /v1/webhooks`;
read the feed with `GET /v1/events`. This is the start of the outbox pattern (dispatcher with
retries is the next milestone).
