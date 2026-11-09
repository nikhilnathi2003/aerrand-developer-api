import uuid
from datetime import datetime, timezone

import mongomock
from django.test import TestCase

from apiv1 import db, reports, wallet

_NS = uuid.UUID("a1b2c3d4-0000-4000-8000-000000000000")


def _owner(name):
    return str(uuid.uuid5(_NS, name.lower()))


class ReportTests(TestCase):
    def setUp(self):
        db.set_db_for_tests(mongomock.MongoClient()["aerrand"])
        self.owner = _owner("Acme")

    def _errand(self, status, price=10.0, paid=True):
        db.errands().insert_one({
            "errand_id": str(uuid.uuid4()),
            "business_owner_id": self.owner,
            "status": status,
            "price": price,
            "payment": {"status": "paid" if paid else "unpaid"},
            "created_at": datetime.now(timezone.utc),
        })

    def test_summary_counts_and_spend(self):
        self._errand("delivered", 10.0)
        self._errand("delivered", 20.0)
        self._errand("pending", 15.0, paid=False)
        wallet.topup(self.owner, 5000)

        s = reports.summary(self.owner)
        self.assertEqual(s["total_errands"], 3)
        self.assertEqual(s["by_status"]["delivered"], 2)
        self.assertEqual(s["delivered_today"], 2)
        self.assertEqual(s["total_spend_cad"], 30.0)   # only paid errands
        self.assertEqual(s["wallet_balance_cad"], 50.0)

    def test_summary_is_scoped_per_business(self):
        self._errand("delivered")
        other = reports.summary(_owner("Other"))
        self.assertEqual(other["total_errands"], 0)
