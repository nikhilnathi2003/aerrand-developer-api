"""Simple prepaid wallet for a business (standalone build).

Balances live in the 'wallets' Mongo collection, keyed by business_owner_id.
Amounts are stored in cents to avoid floating-point errors.
"""
from . import db


def _wallets():
    return db.get_db()["wallets"]


def get_balance(owner_id):
    """Current balance in cents (0 if the business has no wallet yet)."""
    w = _wallets().find_one({"business_owner_id": owner_id})
    return w["balance_cents"] if w else 0


def topup(owner_id, amount_cents):
    """Add funds to a business's wallet. Creates the wallet if needed."""
    _wallets().update_one(
        {"business_owner_id": owner_id},
        {"$inc": {"balance_cents": int(amount_cents)}},
        upsert=True,
    )
    return get_balance(owner_id)


def debit(owner_id, amount_cents):
    """Atomically debit the wallet. Returns True if paid, False if funds are short.

    The condition `balance_cents >= amount` is checked inside the same update, so two
    bookings at once can never overdraw the wallet (race-safe).
    """
    amount_cents = int(amount_cents)
    result = _wallets().update_one(
        {"business_owner_id": owner_id, "balance_cents": {"$gte": amount_cents}},
        {"$inc": {"balance_cents": -amount_cents}},
    )
    return result.modified_count == 1
