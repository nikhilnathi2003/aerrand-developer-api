"""End-to-end tests for the v1 API using an in-memory MongoDB (mongomock).

Run with:  python manage.py test
"""
import json
import uuid

import mongomock
from django.test import TestCase

from apiv1 import db, keys, pricing

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
