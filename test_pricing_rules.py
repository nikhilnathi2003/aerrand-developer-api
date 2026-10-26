from django.test import TestCase

from apiv1 import pricing

PICKUP = {"lat": "42.3149", "lng": "-83.0364"}


def stop(s=0, m=0, l=0):
    return {"lat": "42.28", "lng": "-82.99", "parcels": {"small": s, "medium": m, "large": l}}


class PricingRulesTests(TestCase):
    def test_hst_is_13_percent(self):
        b = pricing.price_route(PICKUP, [stop(2, 1)])
        self.assertEqual(b["hst"], round(b["routePrice"] * 0.13, 2))

    def test_charge_total_is_pretax_plus_hst(self):
        b = pricing.price_route(PICKUP, [stop(2, 1)])
        self.assertEqual(b["chargeTotal"], round(b["routePrice"] + b["hst"], 2))

    def test_small_parcels_are_half_a_cargo_unit(self):
        b = pricing.price_route(PICKUP, [stop(4, 0, 0)])
        self.assertEqual(b["totalCargoUnits"], 2.0)

    def test_big_load_recommends_a_bigger_vehicle(self):
        b = pricing.price_route(PICKUP, [stop(0, 0, 20)])
        self.assertIn(b["recommendedVehicle"], ("van", "truck"))

    def test_over_capacity_is_flagged(self):
        b = pricing.price_route(PICKUP, [stop(0, 0, 30)])
        self.assertTrue(b["overVanCapacity"])
