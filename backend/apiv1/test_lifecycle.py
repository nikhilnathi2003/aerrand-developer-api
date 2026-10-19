from django.test import TestCase

from apiv1 import lifecycle


class LifecycleTests(TestCase):
    def test_can_cancel_before_pickup(self):
        self.assertTrue(lifecycle.can_cancel("pending"))
        self.assertTrue(lifecycle.can_cancel("accepted"))

    def test_cannot_cancel_after_pickup(self):
        self.assertFalse(lifecycle.can_cancel("picked_up"))
        self.assertFalse(lifecycle.can_cancel("delivered"))

    def test_fee_once_driver_accepts(self):
        self.assertEqual(lifecycle.cancellation_fee_cents("accepted", 1104), 276)

    def test_no_fee_before_a_driver_accepts(self):
        self.assertEqual(lifecycle.cancellation_fee_cents("pending", 1104), 0)
