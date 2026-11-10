from django.test import TestCase

from apiv1 import statements


class StatementTests(TestCase):
    def test_low_balance_boundary(self):
        self.assertTrue(statements.is_low(1999))
        self.assertFalse(statements.is_low(2000))
        self.assertFalse(statements.is_low(5000))

    def test_csv_has_header_and_rows(self):
        txns = [
            {"at": "2026-11-01T10:00:00+00:00", "kind": "topup", "amount": 100.0,
             "errand_id": None, "note": "Top-up"},
            {"at": "2026-11-01T11:00:00+00:00", "kind": "charge", "amount": -12.5,
             "errand_id": "e1", "note": "Delivery charge"},
        ]
        csv_text = statements.to_csv(txns)
        lines = [ln for ln in csv_text.splitlines() if ln.strip()]
        self.assertEqual(lines[0], "date,type,amount_cad,errand_id,note")
        self.assertEqual(len(lines), 3)  # header + 2 rows
        self.assertIn("topup", csv_text)
        self.assertIn("-12.5", csv_text)
