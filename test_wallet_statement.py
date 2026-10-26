import mongomock
from django.test import TestCase

from apiv1 import db, wallet


class WalletStatementTests(TestCase):
    def setUp(self):
        db.set_db_for_tests(mongomock.MongoClient()["aerrand"])

    def test_topup_is_recorded(self):
        wallet.topup("b", 5000)
        tx = wallet.transactions("b")
        self.assertEqual(tx[0]["kind"], "topup")
        self.assertEqual(tx[0]["amount"], 50.0)

    def test_charge_is_negative(self):
        wallet.topup("b", 5000)
        wallet.debit("b", 1104)
        charge = [t for t in wallet.transactions("b") if t["kind"] == "charge"][0]
        self.assertTrue(charge["amount"] < 0)

    def test_refund_credits_the_wallet(self):
        wallet.topup("b", 5000)
        wallet.debit("b", 1104)
        before = wallet.get_balance("b")
        wallet.refund("b", 1000)
        self.assertEqual(wallet.get_balance("b"), before + 1000)
