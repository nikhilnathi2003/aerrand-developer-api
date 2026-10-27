from django.test import TestCase

from apiv1 import eta


class EtaTests(TestCase):
    def test_zero_distance_is_at_least_one_minute(self):
        p = {"lat": 42.3, "lng": -83.0}
        self.assertEqual(eta.estimate_minutes(p, p), 1)

    def test_farther_takes_longer(self):
        start = {"lat": 42.30, "lng": -83.00}
        near = eta.estimate_minutes(start, {"lat": 42.31, "lng": -83.00})
        far = eta.estimate_minutes(start, {"lat": 42.40, "lng": -83.00})
        self.assertGreater(far, near)
