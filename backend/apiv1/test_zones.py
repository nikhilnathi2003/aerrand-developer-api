from django.test import TestCase, override_settings

from apiv1 import zones

# A single Windsor zone with a 10 km radius, so the maths is easy to reason about.
_AREAS = [
    {"slug": "windsor", "name": "Windsor", "province": "ON",
     "lat": 42.3149, "lng": -83.0364, "radius_km": 10.0, "active": True},
    {"slug": "leamington", "name": "Leamington", "province": "ON",
     "lat": 42.0536, "lng": -82.5996, "radius_km": 5.0, "active": False},  # inactive
]


@override_settings(SERVICE_AREAS=_AREAS)
class ZoneCheckTests(TestCase):
    def test_point_inside_zone_is_covered(self):
        result = zones.check({"lat": 42.3149, "lng": -83.0364})  # the zone centre
        self.assertTrue(result["in_service_area"])
        self.assertEqual(result["nearest"]["slug"], "windsor")
        self.assertEqual(result["nearest"]["km_outside"], 0)

    def test_point_outside_zone_reports_distance_outside(self):
        # Far north of Windsor, well beyond the 10 km radius.
        result = zones.check({"lat": 42.7000, "lng": -83.0364})
        self.assertFalse(result["in_service_area"])
        self.assertGreater(result["nearest"]["km_outside"], 0)

    def test_inactive_zones_are_ignored(self):
        # Right on the (inactive) Leamington centre — must NOT be treated as covered.
        result = zones.check({"lat": 42.0536, "lng": -82.5996})
        self.assertFalse(result["in_service_area"])
        self.assertEqual(result["nearest"]["slug"], "windsor")
