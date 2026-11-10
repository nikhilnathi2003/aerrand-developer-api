import json
import uuid

import mongomock
from django.test import TestCase

from apiv1 import db, keys, proof, wallet

_NS = uuid.UUID("a1b2c3d4-0000-4000-8000-000000000000")
PICKUP = {"lat": "42.3149", "lng": "-83.0364"}
DROP = {"lat": "42.3201", "lng": "-83.0187",
        "contact": {"name": "Pat", "phone_number": "+15195550000"}}


def _make_key(business="Proof Co"):
    owner = str(uuid.uuid5(_NS, business.lower()))
    plain = keys.generate_key("test")
    db.api_keys().insert_one({
        "id": str(uuid.uuid4()), "business_owner_id": owner, "business_name": business,
        "name": "default", "environment": "test", "key_prefix": keys.prefix_of(plain),
        "key_hash": keys.hash_key(plain), "scopes": ["create", "read", "cancel"],
        "status": "active", "expires_at": None,
    })
    wallet.topup(owner, 10000)
    return plain


class ProofUnitTests(TestCase):
    def test_verify_code_matches_case_insensitive(self):
        self.assertTrue(proof.verify_code("AB12CD", "ab12cd"))
        self.assertTrue(proof.verify_code("AB12CD", " AB12CD "))

    def test_verify_code_rejects_wrong_or_empty(self):
        self.assertFalse(proof.verify_code("AB12CD", "ZZZZZZ"))
        self.assertFalse(proof.verify_code("AB12CD", ""))

    def test_build_record_shape(self):
        rec = proof.build_record("Pat Singh", "left at door")
        self.assertEqual(rec["recipient_name"], "Pat Singh")
        self.assertTrue(rec["code_verified"])
        self.assertIn("confirmed_at", rec)


class ProofEndpointTests(TestCase):
    def setUp(self):
        db.set_db_for_tests(mongomock.MongoClient()["aerrand"])
        self.key = _make_key()

    def _h(self):
        return {"HTTP_AUTHORIZATION": f"Bearer {self.key}"}

    def _create_errand(self):
        q = self.client.post("/v1/quotes", json.dumps({"pickup": PICKUP, "stops": [DROP]}),
                             content_type="application/json", **self._h())
        quote_id = q.json()["quote_id"]
        r = self.client.post("/v1/errands",
                             json.dumps({"quote_id": quote_id, "pickup": PICKUP, "dropoff": DROP}),
                             content_type="application/json", **self._h())
        return r.json()["errand_id"], r.json()["delivery_code"]

    def _advance_to(self, eid, target):
        for _ in range(12):
            r = self.client.post(f"/v1/errands/{eid}/advance", **self._h())
            if r.json().get("status") == target:
                return

    def test_proof_requires_drop_off_stage(self):
        eid, code = self._create_errand()
        r = self.client.post(f"/v1/errands/{eid}/proof",
                             json.dumps({"recipient_name": "Pat", "delivery_code": code}),
                             content_type="application/json", **self._h())
        self.assertEqual(r.status_code, 409)  # not at drop-off yet

    def test_proof_rejects_wrong_code(self):
        eid, _ = self._create_errand()
        self._advance_to(eid, "arrived_dropoff")
        r = self.client.post(f"/v1/errands/{eid}/proof",
                             json.dumps({"recipient_name": "Pat", "delivery_code": "WRONG1"}),
                             content_type="application/json", **self._h())
        self.assertEqual(r.status_code, 422)

    def test_proof_completes_delivery(self):
        eid, code = self._create_errand()
        self._advance_to(eid, "arrived_dropoff")
        r = self.client.post(f"/v1/errands/{eid}/proof",
                             json.dumps({"recipient_name": "Pat Singh", "delivery_code": code}),
                             content_type="application/json", **self._h())
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "delivered")
        self.assertEqual(r.json()["proof_of_delivery"]["recipient_name"], "Pat Singh")
