"""Webhook events — the start of the outbox pattern.

When a delivery changes state we record a **signed** event in `webhook_events`, and a
business registers receiving endpoints in `webhook_endpoints`. Actually delivering each
event to the partner's URL with retries is the dispatcher (next milestone); here we
capture and sign the events and expose them for the business to read.
"""
import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime, timezone

from . import db

# in production each endpoint has its own secret; one shared demo secret here
SIGNING_SECRET = "whsec_demo_secret"

EVENT_CATALOG = [
    "errand.created", "errand.paid", "errand.broadcasted", "errand.accepted",
    "errand.arrived", "errand.picked_up", "errand.in_transit",
    "errand.arrived_dropoff", "errand.delivered", "errand.cancelled",
]


def _endpoints():
    return db.get_db()["webhook_endpoints"]


def _events():
    return db.get_db()["webhook_events"]


def _deliveries():
    return db.get_db()["webhook_deliveries"]


def register(owner, url, events):
    doc = {
        "id": "we_" + uuid.uuid4().hex[:16],
        "business_owner_id": owner,
        "url": url,
        "events": events or ["*"],
        "status": "enabled",
        "created_at": datetime.now(timezone.utc),
    }
    _endpoints().insert_one(doc)
    return {"id": doc["id"], "url": url, "events": doc["events"], "status": "enabled"}


def list_endpoints(owner):
    return [{"id": e["id"], "url": e["url"], "events": e["events"], "status": e.get("status", "enabled")}
            for e in _endpoints().find({"business_owner_id": owner})]


def _sign(body: str) -> str:
    t = int(time.time())
    sig = hmac.new(SIGNING_SECRET.encode(), f"{t}.{body}".encode(), hashlib.sha256).hexdigest()
    return f"t={t},v1={sig}"


def record_event(owner, event_type, errand, extra=None):
    """Build the public event, sign it, and store it (ready for the dispatcher).

    ``extra`` is merged into the event's ``data`` block (e.g. cancellation reason /
    fee outcome for ``errand.cancelled`` per TRD FR-CANCEL-04).
    """
    payload = {
        "id": "evt_" + uuid.uuid4().hex[:16],
        "type": event_type,
        "api_version": "2026-08-29",
        "created": int(time.time()),
        "test_mode": errand.get("test_mode", True),
        "data": {
            "errand_id": errand["errand_id"],
            "status": errand.get("status"),
            "delivery_code": errand.get("delivery_code"),
            "reference": errand.get("reference"),
            **(extra or {}),
        },
    }
    body = json.dumps(payload, separators=(",", ":"))
    _events().insert_one({
        **payload,
        "business_owner_id": owner,
        "signature": _sign(body),
        "at": datetime.now(timezone.utc),
    })
    # fan the event out to the business's subscribed endpoints (delivery log / outbox)
    deliver(owner, event_type, errand)


def deliver(owner, event_type, errand):
    """Record a delivery attempt for each endpoint subscribed to this event type.

    This is the outbox the real dispatcher drains: in test mode the outbound HTTP call
    is simulated and recorded as 'delivered', so the delivery log can be demonstrated
    end to end without a public receiving server.
    """
    delivered = []
    for ep in _endpoints().find({"business_owner_id": owner, "status": "enabled"}):
        subscribed = ep.get("events") or ["*"]
        if "*" not in subscribed and event_type not in subscribed:
            continue
        rec = {
            "id": "whd_" + uuid.uuid4().hex[:16],
            "business_owner_id": owner,
            "endpoint_id": ep["id"],
            "url": ep["url"],
            "event_type": event_type,
            "errand_id": errand.get("errand_id"),
            "status": "delivered",   # simulated success in test mode
            "attempts": 1,
            "at": datetime.now(timezone.utc),
        }
        _deliveries().insert_one(rec)
        delivered.append(rec)
    return delivered


def recent_deliveries(owner, limit=25):
    rows = _deliveries().find({"business_owner_id": owner}).sort("at", -1).limit(limit)
    return [{
        "id": r["id"], "endpoint_id": r["endpoint_id"], "url": r["url"],
        "event_type": r["event_type"], "errand_id": r.get("errand_id"),
        "status": r["status"], "attempts": r["attempts"], "at": r["at"].isoformat(),
    } for r in rows]


def recent_events(owner, limit=20):
    rows = _events().find({"business_owner_id": owner}).sort("at", -1).limit(limit)
    return [{
        "id": r["id"], "type": r["type"], "status": r["data"]["status"],
        "created": r["created"], "signature": r["signature"],
    } for r in rows]
