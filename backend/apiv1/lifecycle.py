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
