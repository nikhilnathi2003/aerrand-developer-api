"""Focused tests for the tracking + cancel + advance view endpoints (Sai).

These exercise the actual HTTP endpoints (not just the lifecycle module), covering:
  - cancellation preview in the tracking response at each stage
  - cancel endpoint: happy path (from_stage, reason), 409 error code, webhook payload
  - advance endpoint: driver interpolation uses progress.position_at, terminal stops
"""
import json
import uuid

import mongomock
from django.test import TestCase

from apiv1 import db, keys, wallet, webhooks

_NS = uuid.UUID("a1b2c3d4-0000-4000-8000-000000000000")
PICKUP = {"lat": "42.3149", "lng": "-83.0364"}
DROP = {"lat": "42.3201", "lng": "-83.0187", "parcels": {"small": 2, "medium": 1}}


def _issue_key(business):
    owner = str(uuid.uuid5(_NS, business.lower()))
    plain = keys.generate_key("test")
    db.api_keys().insert_one({
        "id": str(uuid.uuid4()), "business_owner_id": owner, "business_name": business,
        "name": "default", "environment": "test", "key_prefix": keys.prefix_of(plain),
        "key_hash": keys.hash_key(plain),
        "scopes": ["create", "read", "cancel"], "status": "active", "expires_at": None,
    })
    wallet.topup(owner, 10000)
    return plain, owner


class SaiViewTests(TestCase):
    def setUp(self):
        db.set_db_for_tests(mongomock.MongoClient()["aerrand"])
        self.key, self.owner = _issue_key("Acme Co")

    def _h(self):
        return {"HTTP_AUTHORIZATION": f"Bearer {self.key}"}

    def _create(self):
        q = self.client.post("/v1/quotes",
                             json.dumps({"pickup": PICKUP, "stops": [DROP]}),
                             content_type="application/json", **self._h())
        body = {"quote_id": q.json()["quote_id"], "pickup": PICKUP,
                "dropoff": {"lat": DROP["lat"], "lng": DROP["lng"],
                            "contact": {"name": "Jordan", "phone_number": "+15195550188"}}}
        r = self.client.post("/v1/errands", json.dumps(body),
                             content_type="application/json", **self._h())
        return r.json()["errand_id"]

    def _advance_to(self, eid, target):
        for _ in range(10):
            r = self.client.post(f"/v1/errands/{eid}/advance", **self._h())
            if r.json().get("status") == target:
                return
        raise AssertionError(f"never reached {target}")

    def _track(self, eid):
        return self.client.get(f"/v1/errands/{eid}/tracking", **self._h()).json()

    # ---------- tracking response shape ----------

    def test_tracking_returns_cancellation_preview(self):
        eid = self._create()
        t = self._track(eid)
        self.assertIn("cancellation", t)
        self.assertIn("allowed", t["cancellation"])
        self.assertIn("fee_cents", t["cancellation"])
        self.assertIn("refund_cents", t["cancellation"])

    def test_cancellation_preview_free_before_dispatch(self):
        eid = self._create()
        c = self._track(eid)["cancellation"]
        self.assertTrue(c["allowed"])
        self.assertEqual(c["fee_cents"], 0)
        # Refund equals the full paid total before any fee kicks in.
        self.assertGreater(c["refund_cents"], 0)

    def test_cancellation_preview_charges_fee_after_accept(self):
        from datetime import datetime, timedelta, timezone
        eid = self._create()
        self._advance_to(eid, "accepted")
        # Backdate the "accepted" timeline row past the grace window so the fee kicks in.
        past = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        db.errands().update_one(
            {"errand_id": eid, "timeline.status": "accepted"},
            {"$set": {"timeline.$.at": past}},
        )
        c = self._track(eid)["cancellation"]
        self.assertTrue(c["allowed"])
        self.assertEqual(c["grace_seconds_remaining"], 0)
        # 25% of the paid total.
        paid = c["fee_cents"] + c["refund_cents"]
        self.assertEqual(c["fee_cents"], round(paid * 0.25))

    def test_cancellation_preview_blocked_after_pickup(self):
        eid = self._create()
        self._advance_to(eid, "picked_up")
        c = self._track(eid)["cancellation"]
        self.assertFalse(c["allowed"])
        self.assertEqual(c["fee_cents"], 0)

    def test_tracking_returns_eta_at_timestamp(self):
        eid = self._create()
        self._advance_to(eid, "in_transit")
        t = self._track(eid)
        self.assertIsNotNone(t["eta_minutes"])
        self.assertIsNotNone(t["eta_at"])
        self.assertRegex(t["eta_at"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

    # ---------- cancel endpoint ----------

    def test_cancel_response_includes_from_stage_and_reason(self):
        eid = self._create()
        self._advance_to(eid, "accepted")
        r = self.client.post(f"/v1/errands/{eid}/cancel", **self._h())
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(body["status"], "cancelled")
        self.assertEqual(body["from_stage"], "accepted")
        self.assertEqual(body["reason"], "business_request")

    def test_cancel_error_code_matches_trd(self):
        eid = self._create()
        self._advance_to(eid, "picked_up")
        r = self.client.post(f"/v1/errands/{eid}/cancel", **self._h())
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r.json()["error"]["code"], "cancellation_not_allowed")

    def test_cancel_webhook_carries_reason_and_fee(self):
        eid = self._create()
        self._advance_to(eid, "accepted")
        self.client.post(f"/v1/errands/{eid}/cancel", **self._h())
        # recent_events trims the payload; read the stored event directly for the full data block.
        cancelled = db.get_db()["webhook_events"].find_one(
            {"business_owner_id": self.owner, "type": "errand.cancelled"})
        self.assertIsNotNone(cancelled)
        self.assertEqual(cancelled["data"]["reason"], "business_request")
        self.assertEqual(cancelled["data"]["from_stage"], "accepted")
        self.assertIn("fee", cancelled["data"])
        self.assertIn("refund", cancelled["data"])

    # ---------- advance endpoint ----------

    def test_advance_moves_driver_from_pickup_toward_dropoff(self):
        eid = self._create()
        self._advance_to(eid, "accepted")
        d1 = self._track(eid)["driver"]
        self._advance_to(eid, "in_transit")
        d2 = self._track(eid)["driver"]
        # At "accepted" the driver sits at the pickup; by "in_transit" they've moved toward the drop-off.
        self.assertAlmostEqual(d1["lat"], float(PICKUP["lat"]), places=4)
        drop_lat = float(DROP["lat"])
        self.assertLess(abs(d2["lat"] - drop_lat), abs(d1["lat"] - drop_lat))

    def test_advance_refuses_after_delivered(self):
        eid = self._create()
        self._advance_to(eid, "delivered")
        r = self.client.post(f"/v1/errands/{eid}/advance", **self._h())
        self.assertEqual(r.status_code, 400)

    def test_advance_refuses_after_cancel(self):
        eid = self._create()
        self.client.post(f"/v1/errands/{eid}/cancel", **self._h())
        r = self.client.post(f"/v1/errands/{eid}/advance", **self._h())
        self.assertEqual(r.status_code, 400)

    # ---------- grace window + custom reason (per Aerrand office hours) ----------

    def test_grace_window_keeps_cancel_free_right_after_accept(self):
        eid = self._create()
        self._advance_to(eid, "accepted")
        # Still within the 30-second grace window — fee should be waived.
        c = self._track(eid)["cancellation"]
        self.assertEqual(c["fee_cents"], 0)
        self.assertGreater(c["grace_seconds_remaining"], 0)
        r = self.client.post(f"/v1/errands/{eid}/cancel", **self._h())
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["fee"], 0.0)

    def test_cancel_accepts_custom_reason_from_the_business(self):
        eid = self._create()
        body = json.dumps({"reason": "customer_changed_mind"})
        r = self.client.post(f"/v1/errands/{eid}/cancel", body,
                             content_type="application/json", **self._h())
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["reason"], "customer_changed_mind")
        cancelled = db.get_db()["webhook_events"].find_one(
            {"business_owner_id": self.owner, "type": "errand.cancelled"})
        self.assertEqual(cancelled["data"]["reason"], "customer_changed_mind")

    def test_cancel_is_idempotent_with_same_key(self):
        eid = self._create()
        hdr = {**self._h(), "HTTP_IDEMPOTENCY_KEY": "cancel-xyz-1"}
        r1 = self.client.post(f"/v1/errands/{eid}/cancel", **hdr)
        self.assertEqual(r1.status_code, 200)
        # Replay returns the same response and does NOT emit a second webhook event.
        r2 = self.client.post(f"/v1/errands/{eid}/cancel", **hdr)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.get("Idempotent-Replayed"), "true")
        self.assertEqual(r1.json(), r2.json())
        events = list(db.get_db()["webhook_events"].find(
            {"business_owner_id": self.owner, "type": "errand.cancelled"}))
        self.assertEqual(len(events), 1)

    def test_grace_helper_returns_zero_once_window_elapses(self):
        from apiv1 import lifecycle
        from datetime import datetime, timedelta, timezone
        when = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        timeline = [{"status": "accepted", "at": when.isoformat()}]
        self.assertGreater(lifecycle.accept_grace_remaining(timeline, when), 0)
        self.assertEqual(lifecycle.accept_grace_remaining(timeline, when + timedelta(seconds=60)), 0)

    # ---------- proof of delivery (POST /v1/errands/{id}/proof) ----------

    def _advance_and_capture_code(self, target):
        eid = self._create()
        self._advance_to(eid, target)
        code = self._track(eid)["delivery_code"]
        return eid, code

    def test_proof_happy_path_flips_to_delivered(self):
        eid, code = self._advance_and_capture_code("arrived_dropoff")
        r = self.client.post(f"/v1/errands/{eid}/proof",
                             json.dumps({"delivery_code": code, "recipient_name": "Pat Singh"}),
                             content_type="application/json", **self._h())
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "delivered")
        self.assertEqual(r.json()["proof_of_delivery"]["recipient_name"], "Pat Singh")
        self.assertTrue(r.json()["proof_of_delivery"]["code_verified"])
        # tracking now surfaces the record
        self.assertEqual(self._track(eid)["proof_of_delivery"]["recipient_name"], "Pat Singh")
        # an errand.delivered webhook landed
        delivered = db.get_db()["webhook_events"].find_one(
            {"business_owner_id": self.owner, "type": "errand.delivered"})
        self.assertIsNotNone(delivered)

    def test_proof_rejects_wrong_delivery_code(self):
        eid, _ = self._advance_and_capture_code("arrived_dropoff")
        r = self.client.post(f"/v1/errands/{eid}/proof",
                             json.dumps({"delivery_code": "WRONG1", "recipient_name": "Pat Singh"}),
                             content_type="application/json", **self._h())
        self.assertEqual(r.status_code, 422)
        self.assertEqual(r.json()["error"]["code"], "delivery_code_mismatch")

    def test_proof_rejects_before_dropoff(self):
        eid = self._create()
        self._advance_to(eid, "accepted")
        code = self._track(eid)["delivery_code"]
        r = self.client.post(f"/v1/errands/{eid}/proof",
                             json.dumps({"delivery_code": code, "recipient_name": "Pat Singh"}),
                             content_type="application/json", **self._h())
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r.json()["error"]["code"], "proof_not_allowed")

    def test_proof_requires_recipient_name(self):
        eid, code = self._advance_and_capture_code("arrived_dropoff")
        r = self.client.post(f"/v1/errands/{eid}/proof",
                             json.dumps({"delivery_code": code, "recipient_name": ""}),
                             content_type="application/json", **self._h())
        self.assertEqual(r.status_code, 400)

    # ---------- multi-stop cancellation (TRD FR-CANCEL-02) ----------

    def _create_batch(self):
        """Create a 2-drop-off batch booking and return the two errand_ids."""
        q = self.client.post("/v1/quotes",
                             json.dumps({"pickup": PICKUP, "stops": [DROP, DROP]}),
                             content_type="application/json", **self._h())
        body = {"quote_id": q.json()["quote_id"], "pickup": PICKUP,
                "dropoffs": [
                    {"lat": DROP["lat"], "lng": DROP["lng"],
                     "contact": {"name": "Jordan", "phone_number": "+15195550188"}},
                    {"lat": DROP["lat"], "lng": DROP["lng"],
                     "contact": {"name": "Alex", "phone_number": "+15195550199"}},
                ]}
        r = self.client.post("/v1/errands", json.dumps(body),
                             content_type="application/json", **self._h())
        self.assertEqual(r.status_code, 201)
        return [stop["errand_id"] for stop in r.json()["stops"]]

    def test_batch_cancel_cancels_every_sibling_atomically(self):
        ids = self._create_batch()
        r = self.client.post(f"/v1/errands/{ids[0]}/cancel", **self._h())
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertIn("batch_id", body)
        self.assertEqual(len(body["cancelled"]), 2)
        self.assertEqual(body["skipped"], [])
        # Both sibling errands are now cancelled in the DB.
        for eid in ids:
            self.assertEqual(self._track(eid)["status"], "cancelled")

    def test_batch_cancel_all_or_nothing_blocks_when_one_stop_is_picked_up(self):
        ids = self._create_batch()
        # Advance the first stop past the point of no return.
        self._advance_to(ids[0], "picked_up")
        r = self.client.post(f"/v1/errands/{ids[0]}/cancel", **self._h())
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r.json()["error"]["code"], "cancellation_not_allowed")
        # Nothing was cancelled — the second stop is still in progress.
        self.assertNotEqual(self._track(ids[1])["status"], "cancelled")
        # Per-stop reasons are surfaced in the error details.
        self.assertIn("stops", r.json()["error"]["details"])

    def test_batch_cancel_partial_true_cancels_the_rest_and_skips_locked(self):
        ids = self._create_batch()
        self._advance_to(ids[0], "picked_up")
        r = self.client.post(f"/v1/errands/{ids[0]}/cancel",
                             json.dumps({"partial": True, "reason": "customer_changed_mind"}),
                             content_type="application/json", **self._h())
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(len(body["cancelled"]), 1)
        self.assertEqual(len(body["skipped"]), 1)
        self.assertEqual(body["skipped"][0]["errand_id"], ids[0])
        # Stop 0 stays in progress; stop 1 is cancelled.
        self.assertEqual(self._track(ids[0])["status"], "picked_up")
        self.assertEqual(self._track(ids[1])["status"], "cancelled")

    def test_proof_persists_optional_note(self):
        eid, code = self._advance_and_capture_code("arrived_dropoff")
        body = {"delivery_code": code, "recipient_name": "Pat Singh", "note": "left at front desk"}
        r = self.client.post(f"/v1/errands/{eid}/proof", json.dumps(body),
                             content_type="application/json", **self._h())
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["proof_of_delivery"]["note"], "left at front desk")
