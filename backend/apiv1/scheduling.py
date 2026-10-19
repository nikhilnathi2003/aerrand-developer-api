"""Validation for scheduled deliveries.

Aerrand accepts a `scheduled_at` time that is no earlier than 5 minutes ago and no more
than 7 days out. An empty value means "as soon as possible" (always allowed).
"""
from datetime import datetime, timedelta, timezone


def parse_iso(value):
    """Parse an ISO-8601 string into an aware UTC datetime (None if empty)."""
    if not value:
        return None
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def validate_scheduled_at(value, now=None):
    """Return (ok, error_message).

    now - 5 min  <=  scheduled_at  <=  now + 7 days.  Empty value = ASAP (ok).
    """
    if not value:
        return True, None
    now = now or datetime.now(timezone.utc)
    try:
        dt = parse_iso(value)
    except ValueError:
        return False, "scheduled_at must be an ISO-8601 date-time"
    if dt < now - timedelta(minutes=5):
        return False, "scheduled_at is in the past"
    if dt > now + timedelta(days=7):
        return False, "scheduled_at is more than 7 days away"
    return True, None
