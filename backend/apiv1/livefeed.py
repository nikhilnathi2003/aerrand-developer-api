"""Active-deliveries feed (Sai — live tracking / deliveries).

A live board of the deliveries that are still moving: everything that isn't delivered or
cancelled yet, with its current stage and how far along the route the driver is. This is
what a partner's own "live operations" screen polls to show in-progress jobs at a glance,
without pulling the full history each time. Scoped to the owning business.
"""
from . import db

# Stages that mean the job is finished — these drop off the live board.
TERMINAL = ("delivered", "cancelled")

# How far along the route each stage is (kept in sync with the tracking view's stages).
_STAGE_FRACTION = {
    "pending": 0.0, "pending_payment": 0.0, "accepted": 0.0, "arrived": 0.05,
    "picked_up": 0.1, "in_transit": 0.6, "arrived_dropoff": 0.95, "delivered": 1.0,
}


def active(owner):
    """This business's in-progress deliveries, newest first."""
    rows = [e for e in db.errands().find({"business_owner_id": owner})
            if e.get("status") not in TERMINAL]
    rows.sort(key=lambda e: str(e.get("created_at", "")), reverse=True)
    return [{
        "errand_id": e["errand_id"],
        "delivery_code": e.get("delivery_code"),
        "status": e.get("status"),
        "progress_percent": round(_STAGE_FRACTION.get(e.get("status"), 0.0) * 100),
        "reference": e.get("reference"),
        "vehicle_type": e.get("vehicle_type"),
    } for e in rows]


def count_active(owner):
    """How many deliveries are currently in progress (for a dashboard tile)."""
    return len(active(owner))
