from django.test import TestCase

from apiv1 import lifecycle


class LifecycleRulesTests(TestCase):
    def test_order_starts_and_ends_correctly(self):
        self.assertEqual(lifecycle.ORDER[0], "pending_payment")
        self.assertEqual(lifecycle.ORDER[-1], "delivered")

    def test_cancellable_before_pickup(self):
        for s in ("pending", "broadcasted", "accepted", "arrived"):
            self.assertTrue(lifecycle.can_cancel(s))

    def test_not_cancellable_after_pickup(self):
        for s in ("picked_up", "in_transit", "delivered"):
            self.assertFalse(lifecycle.can_cancel(s))

    def test_fee_only_after_a_driver_accepts(self):
        self.assertEqual(lifecycle.cancellation_fee_cents("pending", 1000), 0)
        self.assertEqual(lifecycle.cancellation_fee_cents("accepted", 1000), 250)
