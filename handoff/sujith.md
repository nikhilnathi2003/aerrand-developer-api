# Sujith — Scheduled deliveries

**Your area:** quotes + booking. From the office-hours answer, Aerrand wants us to support
**scheduled deliveries**, not only immediate ones. The contract says a `scheduled_at` time must
be no earlier than 5 minutes ago and no more than 7 days out; empty means "as soon as possible".

Your part is a small validation module + tests. Create these **two files**, make sure the tests
pass, and push (steps in [README.md](README.md)).

## File 1 — `backend/apiv1/scheduling.py`

```python
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
```

## File 2 — `backend/apiv1/test_scheduling.py`

```python
from datetime import datetime, timedelta, timezone

from django.test import TestCase

from apiv1 import scheduling

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)


class SchedulingTests(TestCase):
    def test_empty_is_asap(self):
        self.assertEqual(scheduling.validate_scheduled_at("", now=NOW), (True, None))

    def test_within_window_ok(self):
        ok, _ = scheduling.validate_scheduled_at((NOW + timedelta(days=2)).isoformat(), now=NOW)
        self.assertTrue(ok)

    def test_past_is_rejected(self):
        ok, _ = scheduling.validate_scheduled_at((NOW - timedelta(hours=1)).isoformat(), now=NOW)
        self.assertFalse(ok)

    def test_too_far_out_is_rejected(self):
        ok, _ = scheduling.validate_scheduled_at((NOW + timedelta(days=8)).isoformat(), now=NOW)
        self.assertFalse(ok)
```

## What it does (so you can explain it)
- `parse_iso` turns the `scheduled_at` string the partner sends into a real date-time.
- `validate_scheduled_at` enforces the booking window (5 min ago → 7 days out); empty = ASAP.
- The `now=` argument lets the tests pin "now" so they're deterministic.

Next step after this merges: call `validate_scheduled_at(...)` inside the create-delivery view.
