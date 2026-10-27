from django.test import TestCase

from apiv1 import progress

P = {"lat": "42.30", "lng": "-83.00"}
D = {"lat": "42.40", "lng": "-83.20"}


class ProgressTests(TestCase):
    def test_zero_is_at_pickup(self):
        self.assertEqual(progress.position_at(P, D, 0), {"lat": 42.30, "lng": -83.00})

    def test_one_is_at_dropoff(self):
        self.assertEqual(progress.position_at(P, D, 1), {"lat": 42.40, "lng": -83.20})

    def test_half_is_the_midpoint(self):
        mid = progress.position_at(P, D, 0.5)
        self.assertEqual(mid["lat"], round((42.30 + 42.40) / 2, 6))
        self.assertEqual(mid["lng"], round((-83.00 + -83.20) / 2, 6))

    def test_fraction_is_clamped_to_the_route(self):
        self.assertEqual(progress.position_at(P, D, 2.0), progress.position_at(P, D, 1))
        self.assertEqual(progress.position_at(P, D, -1.0), progress.position_at(P, D, 0))
