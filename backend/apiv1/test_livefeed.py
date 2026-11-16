import uuid
from datetime import datetime, timezone

import mongomock
from django.test import TestCase

from apiv1 import db, livefeed

_NS = uuid.UUID("a1b2c3d4-0000-4000-8000-000000000000")


def _owner(name):
    return str(uuid.uuid5(_NS, name.lower()))


class LiveFeedTests(TestCase):
    def setUp(self):
        db.set_db_for_tests(mongomock.MongoClient()["aerrand"])
        self.owner = _owner("Acme")

    def _errand(self, status, code="ABC123"):
        db.errands().insert_one({
            "errand_id": str(uuid.uuid4()),
            "business_owner_id": self.owner,
            "status": status,
            "delivery_code": code,
            "created_at": datetime.now(timezone.utc),
        })

    def test_only_in_progress_are_listed(self):
        self._errand("in_transit")
        self._errand("accepted")
        self._errand("delivered")   # finished — should not appear
        self._errand("cancelled")   # finished — should not appear
        feed = livefeed.active(self.owner)
        self.assertEqual(len(feed), 2)
        self.assertEqual({r["status"] for r in feed}, {"in_transit", "accepted"})

    def test_progress_percent_reflects_stage(self):
        self._errand("in_transit")
        self.assertEqual(livefeed.active(self.owner)[0]["progress_percent"], 60)

    def test_scoped_per_business(self):
        self._errand("in_transit")
        self.assertEqual(livefeed.active(_owner("Other")), [])
        self.assertEqual(livefeed.count_active(self.owner), 1)
