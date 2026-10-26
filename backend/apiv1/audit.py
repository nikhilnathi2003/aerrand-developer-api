"""Audit log for API-key actions.

Every key action (created, rotated, revoked) is written to the 'api_audit_log'
collection, so there's a trail of who did what and when. This supports secure API
access — you can see exactly when a key was issued or killed.
"""
from datetime import datetime, timezone

from . import db


def log(action, *, business=None, key_prefix=None, actor="dashboard", detail=""):
    db.get_db()["api_audit_log"].insert_one({
        "action": action,              # key.created / key.rotated / key.revoked
        "business": business,
        "key_prefix": key_prefix,
        "actor": actor,
        "detail": detail,
        "at": datetime.now(timezone.utc),
    })


def recent(limit=20):
    rows = db.get_db()["api_audit_log"].find().sort("at", -1).limit(limit)
    return [{
        "action": r["action"],
        "business": r.get("business"),
        "key_prefix": r.get("key_prefix"),
        "detail": r.get("detail", ""),
        "at": r["at"].isoformat(),
    } for r in rows]
