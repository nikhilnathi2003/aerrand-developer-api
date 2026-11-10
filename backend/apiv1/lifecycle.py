"""Delivery status machine + cancellation rules (from the Aerrand contract).

Status order:
    pending_payment -> pending -> broadcasted -> accepted -> arrived
    -> picked_up -> in_transit -> arrived_dropoff -> delivered
Terminal: cancelled.

A delivery can't be cancelled once the driver has picked it up. Before pickup, a
cancellation fee applies once a driver has accepted/arrived — with a short grace
window right after accept where cancellation is still free (per Aerrand office hours).
"""
from datetime import datetime

ORDER = [
    "pending_payment", "pending", "broadcasted", "accepted", "arrived",
    "picked_up", "in_transit", "arrived_dropoff", "delivered",
]

# once the driver has the parcel (or it's already finished), no cancelling
NO_CANCEL_FROM = {"picked_up", "in_transit", "arrived_dropoff", "delivered", "cancelled"}

# Seconds after a driver accepts during which cancellation is still free.
ACCEPT_GRACE_SECONDS = 30


def can_cancel(status):
    """True if a delivery in this status may still be cancelled."""
    return status not in NO_CANCEL_FROM


def cancellation_fee_cents(status, charge_total_cents):
    """No fee before a driver accepts; a flat 25% fee once accepted/arrived.

    Grace-window overrides live in the view (they need the timeline + current time).
    """
    if status in ("accepted", "arrived"):
        return round(charge_total_cents * 0.25)
    return 0


def accept_grace_remaining(timeline, now):
    """Seconds left in the post-accept grace window (0 once it's elapsed or hasn't opened).

    ``timeline`` is the stored list of ``{"status", "at"}`` rows; ``now`` is a tz-aware
    datetime. Pass whatever "now" the view already uses to keep tests deterministic.
    """
    accepted_at = None
    for row in timeline or []:
        if row.get("status") == "accepted":
            accepted_at = row.get("at")
            break
    if not accepted_at:
        return 0
    try:
        when = datetime.fromisoformat(accepted_at)
    except (TypeError, ValueError):
        return 0
    elapsed = (now - when).total_seconds()
    return max(0, ACCEPT_GRACE_SECONDS - int(elapsed))
