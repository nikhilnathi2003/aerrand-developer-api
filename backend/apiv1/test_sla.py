from datetime import datetime, timedelta, timezone

from django.test import TestCase

from apiv1 import sla


def _timeline(minutes):
    base = datetime(2026, 11, 23, 10, 0, 0, tzinfo=timezone.utc)
    return [
        {"status": "pending", "at": base.isoformat()},
        {"status": "delivered", "at": (base + timedelta(minutes=minutes)).isoformat()},
    ]


class SlaTests(TestCase):
    def test_on_time_delivery_meets_sla(self):
        r = sla.check(_timeline(30), 45)
        self.assertTrue(r["met"])
        self.assertEqual(r["minutes_taken"], 30.0)
        self.assertEqual(r["delta_minutes"], -15.0)   # 15 min early

    def test_late_delivery_misses_sla(self):
        r = sla.check(_timeline(60), 45)
        self.assertFalse(r["met"])
        self.assertEqual(r["delta_minutes"], 15.0)     # 15 min late

    def test_not_enough_timeline_data(self):
        self.assertIsNone(sla.check([], 45))
        self.assertIsNone(sla.check([{"status": "pending", "at": "2026-11-23T10:00:00+00:00"}], 45))
