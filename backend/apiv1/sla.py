"""Delivery SLA check (Sai) — was a delivery on time?

A business can promise a delivery window (say, 45 minutes). This compares that promise
against how long the delivery actually took, read from its timeline, and reports whether
it met the SLA and by how many minutes it was early or late. Pure helper, no database —
the tracking/reporting layer can call it for any delivered errand.
"""
from datetime import datetime


def _parse(ts):
    if hasattr(ts, "isoformat"):      # already a datetime
        return ts
    return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))


def minutes_taken(timeline):
    """Minutes from the first to the last timeline entry, or None if there isn't enough."""
    if not timeline or len(timeline) < 2:
        return None
    start, end = _parse(timeline[0]["at"]), _parse(timeline[-1]["at"])
    return round((end - start).total_seconds() / 60, 1)


def check(timeline, promised_minutes):
    """Return the SLA outcome for a delivery, or None if it can't be measured.

    {
      "met": bool,                 # True if delivered within the promised window
      "minutes_taken": float,
      "promised_minutes": number,
      "delta_minutes": float,      # negative = early / on time, positive = late
    }
    """
    taken = minutes_taken(timeline)
    if taken is None:
        return None
    delta = round(taken - promised_minutes, 1)
    return {
        "met": delta <= 0,
        "minutes_taken": taken,
        "promised_minutes": promised_minutes,
        "delta_minutes": delta,
    }
