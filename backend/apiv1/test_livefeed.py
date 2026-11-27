import uuid
from datetime import datetime, timezone

import mongomock
from django.test import TestCase

from apiv1 import db, keys, livefeed, wallet

_NS = uuid.UUID("a1b2c3d4-0000-4000-8000-000000000000")


def _owner(name):
    return str(uuid.uuid5(_NS, name.lower()))


def _issue_key(business, scopes=("create", "read", "cancel")):
    owner = _owner(business)
    plain = keys.generate_key("test")
    db.api_keys().insert_one({
        "id": str(uuid.uuid4()), "business_owner_id": owner, "business_name": business,
        "name": "default", "environment": "test", "key_prefix": keys.prefix_of(plain),
        "key_hash": keys.hash_key(plain),
        "scopes": list(scopes), "status": "active", "expires_at": None,
    })
    wallet.topup(owner, 10000)
    return plain, owner


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


class LiveFeedEndpointTests(TestCase):
    """Integration tests for GET /v1/livefeed (the view / URL wiring)."""

    def setUp(self):
        db.set_db_for_tests(mongomock.MongoClient()["aerrand"])
        self.key, self.owner = _issue_key("Acme Co")
        self.other_key, self.other_owner = _issue_key("Other Inc")

    def _h(self, k):
        return {"HTTP_AUTHORIZATION": f"Bearer {k}"}

    def _seed(self, owner, status):
        db.errands().insert_one({
            "errand_id": str(uuid.uuid4()),
            "business_owner_id": owner, "status": status,
            "delivery_code": "ABC123",
            "created_at": datetime.now(timezone.utc),
        })

    def test_returns_count_and_active_rows(self):
        self._seed(self.owner, "in_transit")
        self._seed(self.owner, "accepted")
        self._seed(self.owner, "delivered")   # should not appear
        r = self.client.get("/v1/livefeed", **self._h(self.key))
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["count"], 2)
        self.assertEqual(len(body["active"]), 2)
        # Each row carries a progress_percent (from the stage map).
        self.assertIn("progress_percent", body["active"][0])

    def test_scoped_per_business(self):
        self._seed(self.owner, "in_transit")
        # Acme sees 1; Other Inc sees 0.
        self.assertEqual(self.client.get("/v1/livefeed", **self._h(self.key)).json()["count"], 1)
        self.assertEqual(self.client.get("/v1/livefeed", **self._h(self.other_key)).json()["count"], 0)

    def test_requires_a_key(self):
        r = self.client.get("/v1/livefeed")
        self.assertEqual(r.status_code, 401)
