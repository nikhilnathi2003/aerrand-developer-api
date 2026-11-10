"""Proof of delivery (POD) — capture who received the parcel at the drop-off.

When a delivery reaches the drop-off, the driver (or the recipient) confirms it with the
6-character delivery code the sender was given. We verify that code, then record the
recipient's name, an optional note, and a timestamp. This is the auditable proof that a
delivery actually completed, and it is returned on the tracking view.
"""
from datetime import datetime, timezone


def verify_code(expected, provided):
    """True when the provided code matches the errand's delivery code (case-insensitive)."""
    if not provided:
        return False
    return str(provided).strip().upper() == str(expected).strip().upper()


def build_record(recipient_name, note="", code_verified=True):
    """Shape the proof-of-delivery record stored on the errand."""
    return {
        "recipient_name": (recipient_name or "").strip(),
        "note": (note or "").strip(),
        "code_verified": bool(code_verified),
        "confirmed_at": datetime.now(timezone.utc).isoformat(),
    }
