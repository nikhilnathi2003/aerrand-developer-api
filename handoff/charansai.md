# Charan Sai — Simple wallet

**Your area:** payment. Aerrand businesses have a prepaid wallet; a booking should pay itself
from the balance, or fail cleanly if funds are short (from the office-hours answer: "build a
simple wallet; if there isn't enough money, the transaction is cancelled").

Your part is a small, self-contained wallet module + tests. Create these **two files**, make
sure the tests pass, and push (steps in [README.md](README.md)).

## File 1 — `backend/apiv1/wallet.py`

```python
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
```

## File 2 — `backend/apiv1/test_wallet.py`

```python
import mongomock
from django.test import TestCase

from apiv1 import db, wallet


class WalletTests(TestCase):
    def setUp(self):
        db.set_db_for_tests(mongomock.MongoClient()["aerrand"])

    def test_topup_and_balance(self):
        wallet.topup("biz1", 5000)
        self.assertEqual(wallet.get_balance("biz1"), 5000)

    def test_debit_success(self):
        wallet.topup("biz1", 5000)
        self.assertTrue(wallet.debit("biz1", 1104))
        self.assertEqual(wallet.get_balance("biz1"), 3896)

    def test_debit_insufficient_funds(self):
        wallet.topup("biz1", 500)
        self.assertFalse(wallet.debit("biz1", 1104))
        self.assertEqual(wallet.get_balance("biz1"), 500)  # unchanged
```

## What it does (so you can explain it)
- `get_balance` / `topup` — read and add funds (in cents).
- `debit` — subtracts the charge **only if** the balance covers it, in one atomic database
  operation, so it's safe even if two bookings happen at once. Returns False when funds are
  short — that's the "transaction is cancelled" case Johnpaul described.

Next step after this merges: call `wallet.debit(...)` when a delivery is created.
