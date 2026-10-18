# Sai Srinivas — Lifecycle + cancellation rules

**Your area:** tracking + cancellation. From the office-hours answer: a delivery **can't be
cancelled once the driver has picked it up**; before that, a cancellation fee applies once a
driver is assigned. This module holds the status order and those cancellation rules.

Your part is a small module + tests. Create these **two files**, make sure the tests pass, and
push (steps in [README.md](README.md)).

## File 1 — `backend/apiv1/lifecycle.py`

```python
"""Delivery status machine + cancellation rules (from the Aerrand contract).

Status order:
    pending_payment -> pending -> broadcasted -> accepted -> arrived
    -> picked_up -> in_transit -> arrived_dropoff -> delivered
Terminal: cancelled.

A delivery can't be cancelled once the driver has picked it up. Before pickup, a
cancellation fee applies once a driver has accepted/arrived.
"""

ORDER = [
    "pending_payment", "pending", "broadcasted", "accepted", "arrived",
    "picked_up", "in_transit", "arrived_dropoff", "delivered",
]

# once the driver has the parcel (or it's already finished), no cancelling
NO_CANCEL_FROM = {"picked_up", "in_transit", "arrived_dropoff", "delivered", "cancelled"}


def can_cancel(status):
    """True if a delivery in this status may still be cancelled."""
    return status not in NO_CANCEL_FROM


def cancellation_fee_cents(status, charge_total_cents):
    """No fee before a driver accepts; a flat 25% fee once accepted/arrived."""
    if status in ("accepted", "arrived"):
        return round(charge_total_cents * 0.25)
    return 0
```

## File 2 — `backend/apiv1/test_lifecycle.py`

```python
from django.test import TestCase

from apiv1 import lifecycle


class LifecycleTests(TestCase):
    def test_can_cancel_before_pickup(self):
        self.assertTrue(lifecycle.can_cancel("pending"))
        self.assertTrue(lifecycle.can_cancel("accepted"))

    def test_cannot_cancel_after_pickup(self):
        self.assertFalse(lifecycle.can_cancel("picked_up"))
        self.assertFalse(lifecycle.can_cancel("delivered"))

    def test_fee_once_driver_accepts(self):
        self.assertEqual(lifecycle.cancellation_fee_cents("accepted", 1104), 276)

    def test_no_fee_before_a_driver_accepts(self):
        self.assertEqual(lifecycle.cancellation_fee_cents("pending", 1104), 0)
```

## What it does (so you can explain it)
- `can_cancel` — returns False once the driver has picked up (or it's delivered/cancelled),
  which is exactly the rule Johnpaul gave.
- `cancellation_fee_cents` — no fee if cancelled before a driver accepts; a 25% fee once a
  driver is on the way. (276 = 25% of 1104 cents.)

Next step after this merges: use these in a `POST /v1/errands/{id}/cancel` endpoint.
