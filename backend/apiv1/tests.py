"""End-to-end tests for the v1 API using an in-memory MongoDB (mongomock).

Run with:  python manage.py test
"""
import json
import uuid

import mongomock
from django.test import TestCase

from apiv1 import db, keys, pricing, wallet

_NS = uuid.UUID("a1b2c3d4-0000-4000-8000-000000000000")
WINDSOR_PICKUP = {"lat": "42.3149", "lng": "-83.0364"}
STOP1 = {"lat": "42.3201", "lng": "-83.0187", "parcels": {"small": 2, "medium": 1}}


def _make_key(business, scopes=("create", "read", "cancel"), env="test"):
    owner = str(uuid.uuid5(_NS, business.lower()))
    plain = keys.generate_key(env)
    db.api_keys().insert_one({
        "id": str(uuid.uuid4()), "business_owner_id": owner, "business_name": business,
        "name": "default", "environment": env, "key_prefix": keys.prefix_of(plain),
        "key_hash": keys.hash_key(plain), "scopes": list(scopes), "status": "active",
        "expires_at": None,
    })
    wallet.topup(owner, 10000)  # fund the test wallet so bookings can pay
    return plain


class ApiFlowTests(TestCase):
    def setUp(self):
        db.set_db_for_tests(mongomock.MongoClient()["aerrand"])
        self.acme = _make_key("Acme Co")
        self.other = _make_key("Other Inc")
        self.readonly = _make_key("Acme Co", scopes=("read",))

    def _h(self, k):
        return {"HTTP_AUTHORIZATION": f"Bearer {k}"}

    # --- pricing ---
    def test_pricing_matches_contract_components(self):
        bd = pricing.price_route(
            WINDSOR_PICKUP,
            [STOP1, {"lat": "42.2789", "lng": "-82.9912", "parcels": {"small": 4}}],
        )
        self.assertEqual(bd["dropBaseTotal"], 11.50)
        self.assertEqual(bd["sizeAddOnTotal"], 2.00)
        self.assertEqual(bd["totalCargoUnits"], 4.0)
        self.assertEqual(bd["recommendedVehicle"], "motorcycle")

    # --- auth ---
    def test_no_key_unauthorized(self):
        r = self.client.post("/v1/quotes",
                             json.dumps({"pickup": WINDSOR_PICKUP, "stops": [STOP1]}),
                             content_type="application/json")
        self.assertEqual(r.status_code, 401)

    def test_revoked_key_unauthorized(self):
        db.api_keys().update_one({"key_prefix": keys.prefix_of(self.acme)},
                                 {"$set": {"status": "revoked"}})
        r = self.client.post("/v1/quotes",
                             json.dumps({"pickup": WINDSOR_PICKUP, "stops": [STOP1]}),
                             content_type="application/json", **self._h(self.acme))
        self.assertEqual(r.status_code, 401)

    # --- full flow ---
    def _quote(self):
        r = self.client.post("/v1/quotes",
                             json.dumps({"pickup": WINDSOR_PICKUP, "stops": [STOP1]}),
                             content_type="application/json", **self._h(self.acme))
        self.assertEqual(r.status_code, 200)
        return r.json()["quote_id"]

    def test_quote_create_read(self):
        quote_id = self._quote()
        body = {"quote_id": quote_id, "pickup": WINDSOR_PICKUP,
                "dropoff": {"lat": "42.3201", "lng": "-83.0187",
                            "contact": {"name": "Jordan", "phone_number": "+15195550188"},
                            "preference": "leave_at_door"}}
        r = self.client.post("/v1/errands", json.dumps(body),
                             content_type="application/json", **self._h(self.acme))
        self.assertEqual(r.status_code, 201)
        errand = r.json()
        self.assertTrue(errand["errand_id"])
        self.assertTrue(errand["delivery_code"])
        self.assertTrue(errand["test_mode"])

        eid = errand["errand_id"]
        self.assertEqual(self.client.get(f"/v1/errands/{eid}", **self._h(self.acme)).status_code, 200)
        # tenant isolation
        self.assertEqual(self.client.get(f"/v1/errands/{eid}", **self._h(self.other)).status_code, 404)

    def test_create_requires_create_scope(self):
        quote_id = self._quote()
        body = {"quote_id": quote_id, "pickup": WINDSOR_PICKUP,
                "dropoff": {"lat": "42.3201", "lng": "-83.0187",
                            "contact": {"name": "Jordan", "phone_number": "+15195550188"}}}
        r = self.client.post("/v1/errands", json.dumps(body),
                             content_type="application/json", **self._h(self.readonly))
        self.assertEqual(r.status_code, 403)

    # --- helpers for the newer features ---
    def _acme_owner(self):
        return str(uuid.uuid5(_NS, "acme co"))

    def _create(self):
        quote_id = self._quote()
        body = {"quote_id": quote_id, "pickup": WINDSOR_PICKUP,
                "dropoff": {"lat": "42.3201", "lng": "-83.0187",
                            "contact": {"name": "Jordan", "phone_number": "+15195550188"}}}
        r = self.client.post("/v1/errands", json.dumps(body),
                             content_type="application/json", **self._h(self.acme))
        self.assertEqual(r.status_code, 201)
        return r.json()["errand_id"]

    def _advance_to(self, eid, target):
        for _ in range(10):
            r = self.client.post(f"/v1/errands/{eid}/advance", **self._h(self.acme))
            if r.json().get("status") == target:
                return

    # --- wallet (Charan) ---
    def test_booking_charges_wallet(self):
        owner = self._acme_owner()
        before = wallet.get_balance(owner)
        self._create()
        self.assertLess(wallet.get_balance(owner), before)

    def test_insufficient_funds(self):
        owner = self._acme_owner()
        wallet.debit(owner, wallet.get_balance(owner) - 100)  # leave $1
        quote_id = self._quote()
        body = {"quote_id": quote_id, "pickup": WINDSOR_PICKUP,
                "dropoff": {"lat": "42.3201", "lng": "-83.0187",
                            "contact": {"name": "Jordan", "phone_number": "+15195550188"}}}
        r = self.client.post("/v1/errands", json.dumps(body),
                             content_type="application/json", **self._h(self.acme))
        self.assertEqual(r.status_code, 402)

    # --- tracking / cancel (Sai) ---
    def test_cancel_before_pickup_refunds(self):
        eid = self._create()
        r = self.client.post(f"/v1/errands/{eid}/cancel", **self._h(self.acme))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "cancelled")

    def test_cannot_cancel_after_pickup(self):
        eid = self._create()
        self._advance_to(eid, "picked_up")
        r = self.client.post(f"/v1/errands/{eid}/cancel", **self._h(self.acme))
        self.assertEqual(r.status_code, 409)

    def test_advance_adds_driver(self):
        eid = self._create()
        self._advance_to(eid, "accepted")
        r = self.client.get(f"/v1/errands/{eid}/tracking", **self._h(self.acme))
        self.assertIsNotNone(r.json()["driver"])

    # --- webhooks (team) ---
    def test_webhook_events_recorded(self):
        self._create()
        r = self.client.get("/v1/events", **self._h(self.acme))
        types = [e["type"] for e in r.json()["events"]]
        self.assertIn("errand.created", types)
        self.assertTrue(all(e["signature"].startswith("t=") for e in r.json()["events"]))

    def test_webhook_register_requires_https(self):
        r = self.client.post("/v1/webhooks", json.dumps({"url": "http://x.com"}),
                             content_type="application/json", **self._h(self.acme))
        self.assertEqual(r.status_code, 400)

    # --- wallet statement (Charan) ---
    def test_wallet_records_transactions(self):
        self._create()
        r = self.client.get("/v1/wallet", **self._h(self.acme))
        kinds = [t["kind"] for t in r.json()["transactions"]]
        self.assertIn("charge", kinds)

    # --- driver moves (Sai) ---
    def test_driver_moves_toward_dropoff(self):
        eid = self._create()
        self._advance_to(eid, "in_transit")
        r = self.client.get(f"/v1/errands/{eid}/tracking", **self._h(self.acme))
        self.assertIsNotNone(r.json()["driver"])
        self.assertIsNotNone(r.json()["eta_minutes"])

    # --- key rotation (Nikhil) ---
    def test_rotate_key_kills_old_key(self):
        k = self.client.post("/v1/keys", json.dumps({"business": "Rotate Co"}),
                             content_type="application/json").json()["key"]
        q = {"pickup": WINDSOR_PICKUP, "stops": [STOP1]}
        self.assertEqual(self.client.post("/v1/quotes", json.dumps(q),
                         content_type="application/json", **self._h(k)).status_code, 200)
        self.client.post("/v1/keys/rotate", json.dumps({"prefix": keys.prefix_of(k)}),
                         content_type="application/json")
        self.assertEqual(self.client.post("/v1/quotes", json.dumps(q),
                         content_type="application/json", **self._h(k)).status_code, 401)


class IdempotencyTests(TestCase):
    def setUp(self):
        db.set_db_for_tests(mongomock.MongoClient()["aerrand"])
        self.key = _make_key("Acme Co")

    def _h(self, extra=None):
        h = {"HTTP_AUTHORIZATION": f"Bearer {self.key}"}
        if extra:
            h.update(extra)
        return h

    def _quote(self):
        return self.client.post("/v1/quotes",
            json.dumps({"pickup": WINDSOR_PICKUP, "stops": [STOP1]}),
            content_type="application/json", **self._h()).json()["quote_id"]

    def test_replay_returns_same_delivery(self):
        body = {"quote_id": self._quote(),
                "dropoff": {"lat": "42.28", "lng": "-82.99",
                            "contact": {"name": "J", "phone_number": "+1"}}}
        h = self._h({"HTTP_IDEMPOTENCY_KEY": "abc-123"})
        r1 = self.client.post("/v1/errands", json.dumps(body), content_type="application/json", **h)
        r2 = self.client.post("/v1/errands", json.dumps(body), content_type="application/json", **h)
        self.assertEqual(r1.status_code, 201)
        self.assertEqual(r2.status_code, 201)
        self.assertEqual(r1.json()["errand_id"], r2.json()["errand_id"])  # no duplicate
        self.assertEqual(db.errands().count_documents({}), 1)

    def test_same_key_different_body_is_422(self):
        h = self._h({"HTTP_IDEMPOTENCY_KEY": "dup-key"})
        b1 = {"quote_id": self._quote(),
              "dropoff": {"lat": "42.28", "lng": "-82.99", "contact": {"name": "A", "phone_number": "+1"}}}
        self.client.post("/v1/errands", json.dumps(b1), content_type="application/json", **h)
        b2 = {"quote_id": self._quote(),
              "dropoff": {"lat": "42.28", "lng": "-82.99", "contact": {"name": "B", "phone_number": "+2"}}}
        r = self.client.post("/v1/errands", json.dumps(b2), content_type="application/json", **h)
        self.assertEqual(r.status_code, 422)
