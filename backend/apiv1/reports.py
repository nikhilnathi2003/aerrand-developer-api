"""Business reporting — a quick operational summary of a business's deliveries.

Aggregates the business's own errands: how many there are, a breakdown by status, how
many were delivered today, total spend, and the current wallet balance. Scoped to the
owning business (tenant isolation).
"""
from collections import Counter
from datetime import datetime, timezone

from . import db, wallet


def summary(owner):
    errs = list(db.errands().find({"business_owner_id": owner}))
    by_status = Counter(e.get("status", "unknown") for e in errs)

    today = datetime.now(timezone.utc).date()
    delivered_today = sum(
        1 for e in errs
        if e.get("status") == "delivered"
        and e.get("created_at") and _as_date(e["created_at"]) == today
    )

    total_spend = sum(
        e.get("price", 0) for e in errs
        if (e.get("payment") or {}).get("status") == "paid"
    )

    return {
        "total_errands": len(errs),
        "by_status": dict(by_status),
        "delivered_today": delivered_today,
        "total_spend_cad": round(total_spend, 2),
        "wallet_balance_cad": round(wallet.get_balance(owner) / 100, 2),
    }


def _as_date(value):
    """created_at is a datetime; be tolerant of a string if one slips in."""
    if hasattr(value, "date"):
        return value.date()
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
