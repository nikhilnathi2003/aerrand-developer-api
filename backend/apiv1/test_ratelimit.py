from django.test import TestCase

from apiv1.ratelimit import RateLimiter


class _Clock:
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t


class RateLimitTests(TestCase):
    def test_requests_under_the_limit_are_allowed(self):
        rl = RateLimiter(3, 60, clock=_Clock())
        for _ in range(3):
            self.assertTrue(rl.check("k")["allowed"])

    def test_over_the_limit_is_blocked_with_retry_after(self):
        rl = RateLimiter(3, 60, clock=_Clock())
        for _ in range(3):
            rl.check("k")
        d = rl.check("k")
        self.assertFalse(d["allowed"])
        self.assertGreater(d["retry_after"], 0)

    def test_window_resets_after_it_passes(self):
        clock = _Clock()
        rl = RateLimiter(2, 60, clock=clock)
        rl.check("k")
        rl.check("k")
        self.assertFalse(rl.check("k")["allowed"])
        clock.t += 61
        self.assertTrue(rl.check("k")["allowed"])

    def test_keys_are_independent(self):
        rl = RateLimiter(1, 60, clock=_Clock())
        self.assertTrue(rl.check("a")["allowed"])
        self.assertTrue(rl.check("b")["allowed"])
        self.assertFalse(rl.check("a")["allowed"])

    def test_remaining_counts_down(self):
        rl = RateLimiter(3, 60, clock=_Clock())
        self.assertEqual(rl.check("k")["remaining"], 2)
        self.assertEqual(rl.check("k")["remaining"], 1)
        self.assertEqual(rl.check("k")["remaining"], 0)
