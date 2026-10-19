from datetime import datetime, timedelta, timezone

from django.test import TestCase

from apiv1 import scheduling

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)


class SchedulingTests(TestCase):
    def test_empty_is_asap(self):
        self.assertEqual(scheduling.validate_scheduled_at("", now=NOW), (True, None))

    def test_within_window_ok(self):
        ok, _ = scheduling.validate_scheduled_at((NOW + timedelta(days=2)).isoformat(), now=NOW)
        self.assertTrue(ok)

    def test_past_is_rejected(self):
        ok, _ = scheduling.validate_scheduled_at((NOW - timedelta(hours=1)).isoformat(), now=NOW)
        self.assertFalse(ok)

    def test_too_far_out_is_rejected(self):
        ok, _ = scheduling.validate_scheduled_at((NOW + timedelta(days=8)).isoformat(), now=NOW)
        self.assertFalse(ok)
