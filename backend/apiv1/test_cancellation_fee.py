from django.test import TestCase

from apiv1 import lifecycle


class CancellationFeeTests(TestCase):
    def test_no_fee_before_a_driver_accepts(self):
        for s in ("pending_payment", "pending", "broadcasted"):
            self.assertEqual(lifecycle.cancellation_fee_cents(s, 2000), 0)

    def test_quarter_fee_after_accept_or_arrive(self):
        self.assertEqual(lifecycle.cancellation_fee_cents("accepted", 2000), 500)
        self.assertEqual(lifecycle.cancellation_fee_cents("arrived", 2000), 500)

    def test_cannot_cancel_once_picked_up(self):
        self.assertFalse(lifecycle.can_cancel("picked_up"))
        self.assertFalse(lifecycle.can_cancel("in_transit"))

    def test_terminal_states_cannot_cancel(self):
        self.assertFalse(lifecycle.can_cancel("delivered"))
        self.assertFalse(lifecycle.can_cancel("cancelled"))

    def test_can_cancel_up_to_arrival(self):
        for s in ("pending", "broadcasted", "accepted", "arrived"):
            self.assertTrue(lifecycle.can_cancel(s))

    def test_fee_scales_with_the_total(self):
        self.assertEqual(lifecycle.cancellation_fee_cents("accepted", 1604), round(1604 * 0.25))
