import mongomock
from django.test import TestCase

from apiv1 import db, wallet


class WalletTests(TestCase):
    def setUp(self):
        db.set_db_for_tests(mongomock.MongoClient()["aerrand"])

    def test_topup_and_balance(self):
        wallet.topup("biz1", 5000)
        self.assertEqual(wallet.get_balance("biz1"), 5000)

    def test_debit_success(self):
        wallet.topup("biz1", 5000)
        self.assertTrue(wallet.debit("biz1", 1104))
        self.assertEqual(wallet.get_balance("biz1"), 3896)

    def test_debit_insufficient_funds(self):
        wallet.topup("biz1", 500)
        self.assertFalse(wallet.debit("biz1", 1104))
        self.assertEqual(wallet.get_balance("biz1"), 500)  # unchanged
