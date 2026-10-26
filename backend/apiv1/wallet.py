"""Prepaid wallet for a business — balance + full transaction history.

Balances live in the 'wallets' collection; every movement (top-up, charge, refund) is
recorded in 'wallet_transactions' so there's a complete, auditable statement.
Amounts are stored in cents to avoid floating-point errors.
"""
from datetime import datetime, timezone

from . import db


def _wallets():
    return db.get_db()["wallets"]


def _txns():
    return db.get_db()["wallet_transactions"]


def _record(owner, kind, amount_cents, errand_id=None, note=""):
    _txns().insert_one({
        "business_owner_id": owner,
        "kind": kind,                      # topup / charge / refund
        "amount_cents": int(amount_cents),  # +credit / -debit
        "errand_id": errand_id,
        "note": note,
        "at": datetime.now(timezone.utc),
    })


def get_balance(owner_id):
    w = _wallets().find_one({"business_owner_id": owner_id})
    return w["balance_cents"] if w else 0


def topup(owner_id, amount_cents, note="Top-up"):
    amount_cents = int(amount_cents)
    _wallets().update_one({"business_owner_id": owner_id},
                          {"$inc": {"balance_cents": amount_cents}}, upsert=True)
    _record(owner_id, "topup", amount_cents, note=note)
    return get_balance(owner_id)


def debit(owner_id, amount_cents, errand_id=None):
    """Atomically charge the wallet. Returns True if paid, False if funds are short."""
    amount_cents = int(amount_cents)
    result = _wallets().update_one(
        {"business_owner_id": owner_id, "balance_cents": {"$gte": amount_cents}},
        {"$inc": {"balance_cents": -amount_cents}},
    )
    if result.modified_count == 1:
        _record(owner_id, "charge", -amount_cents, errand_id, "Delivery charge")
        return True
    return False


def refund(owner_id, amount_cents, errand_id=None):
    amount_cents = int(amount_cents)
    _wallets().update_one({"business_owner_id": owner_id},
                          {"$inc": {"balance_cents": amount_cents}}, upsert=True)
    _record(owner_id, "refund", amount_cents, errand_id, "Cancellation refund")
    return get_balance(owner_id)


def transactions(owner_id, limit=25):
    rows = _txns().find({"business_owner_id": owner_id}).sort("at", -1).limit(limit)
    return [{
        "kind": r["kind"],
        "amount": round(r["amount_cents"] / 100, 2),
        "errand_id": r.get("errand_id"),
        "note": r.get("note", ""),
        "at": r["at"].isoformat(),
    } for r in rows]
