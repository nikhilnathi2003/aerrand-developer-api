import uuid

import mongomock
from django.test import TestCase

from apiv1 import addresses, db

_NS = uuid.UUID("a1b2c3d4-0000-4000-8000-000000000000")


def _owner(name):
    return str(uuid.uuid5(_NS, name.lower()))


class AddressBookTests(TestCase):
    def setUp(self):
        db.set_db_for_tests(mongomock.MongoClient()["aerrand"])

    def test_save_resolves_a_known_place(self):
        # a preset place resolves offline (no network needed)
        rec = addresses.save(_owner("Acme"), "HQ", "University of Windsor")
        self.assertIsNotNone(rec)
        self.assertEqual(rec["label"], "HQ")
        self.assertTrue(rec["id"].startswith("addr_"))
        self.assertAlmostEqual(rec["lat"], 42.3060, places=2)

    def test_list_is_scoped_per_business(self):
        addresses.save(_owner("Acme"), "HQ", "Devonshire Mall")
        addresses.save(_owner("Other"), "Shop", "St Clair College")
        acme = addresses.list_for(_owner("Acme"))
        self.assertEqual(len(acme), 1)
        self.assertEqual(acme[0]["label"], "HQ")
