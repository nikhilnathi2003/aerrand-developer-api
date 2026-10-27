from django.test import TestCase

from apiv1 import lifecycle


class LifecycleOrderTests(TestCase):
    def test_order_is_a_clean_sequence(self):
        self.assertEqual(lifecycle.ORDER[0], "pending_payment")
        self.assertEqual(lifecycle.ORDER[-1], "delivered")
        self.assertEqual(len(lifecycle.ORDER), len(set(lifecycle.ORDER)))  # no duplicates

    def test_pickup_onwards_cannot_be_cancelled(self):
        for s in ("picked_up", "in_transit", "arrived_dropoff", "delivered"):
            self.assertIn(s, lifecycle.NO_CANCEL_FROM)

    def test_early_states_are_still_cancellable(self):
        for s in ("pending", "broadcasted", "accepted", "arrived"):
            self.assertNotIn(s, lifecycle.NO_CANCEL_FROM)

    def test_cancelled_is_terminal(self):
        self.assertIn("cancelled", lifecycle.NO_CANCEL_FROM)
        self.assertFalse(lifecycle.can_cancel("cancelled"))
