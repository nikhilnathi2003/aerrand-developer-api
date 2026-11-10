import uuid

import mongomock
from django.test import TestCase

from apiv1 import db, webhooks

_NS = uuid.UUID("a1b2c3d4-0000-4000-8000-000000000000")


def _owner(name):
    return str(uuid.uuid5(_NS, name.lower()))


class WebhookDeliveryTests(TestCase):
    def setUp(self):
        db.set_db_for_tests(mongomock.MongoClient()["aerrand"])
        self.owner = _owner("Acme")

    def test_event_is_delivered_to_subscribed_endpoint(self):
        webhooks.register(self.owner, "https://example.com/hook", ["*"])
        webhooks.record_event(self.owner, "errand.created", {"errand_id": "e1", "status": "pending"})
        deliveries = webhooks.recent_deliveries(self.owner)
        self.assertEqual(len(deliveries), 1)
        self.assertEqual(deliveries[0]["event_type"], "errand.created")
        self.assertEqual(deliveries[0]["status"], "delivered")
        self.assertEqual(deliveries[0]["url"], "https://example.com/hook")

    def test_endpoint_only_gets_events_it_subscribed_to(self):
        webhooks.register(self.owner, "https://example.com/paid-only", ["errand.paid"])
        webhooks.record_event(self.owner, "errand.created", {"errand_id": "e1", "status": "pending"})
        self.assertEqual(len(webhooks.recent_deliveries(self.owner)), 0)
        webhooks.record_event(self.owner, "errand.paid", {"errand_id": "e1", "status": "pending"})
        self.assertEqual(len(webhooks.recent_deliveries(self.owner)), 1)

    def test_deliveries_are_scoped_per_business(self):
        webhooks.register(self.owner, "https://example.com/hook", ["*"])
        webhooks.record_event(self.owner, "errand.created", {"errand_id": "e1", "status": "pending"})
        self.assertEqual(len(webhooks.recent_deliveries(_owner("Other"))), 0)
