"""Saved address book — businesses save frequent pickup/drop-off locations by label.

Instead of sending coordinates on every booking, a business saves an address once (we
geocode it to coordinates) and refers to it later by its short id. Every address is
scoped to the owning business (tenant isolation), same as errands and wallets.
"""
import uuid
from datetime import datetime, timezone

from . import db, geocoding


def _col():
    return db.get_db()["saved_addresses"]


def save(owner, label, query):
    """Geocode `query` and store it under `label`. Returns the public record, or None
    if the address could not be resolved."""
    geo = geocoding.geocode(query)
    if not geo:
        return None
    doc = {
        "id": "addr_" + uuid.uuid4().hex[:12],
        "business_owner_id": owner,
        "label": (label or "").strip() or "Saved address",
        "address": query.strip(),
        "lat": geo["lat"],
        "lng": geo["lng"],
        "created_at": datetime.now(timezone.utc),
    }
    _col().insert_one(doc)
    return _public(doc)


def list_for(owner):
    rows = _col().find({"business_owner_id": owner}).sort("created_at", -1)
    return [_public(d) for d in rows]


def _public(d):
    return {
        "id": d["id"],
        "label": d["label"],
        "address": d["address"],
        "lat": d["lat"],
        "lng": d["lng"],
    }
