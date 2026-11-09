from django.test import TestCase

from apiv1 import ratelimit


class RateLimitEnforceTests(TestCase):
    def test_enforce_returns_a_decision(self):
        decision = ratelimit.enforce("some-key-prefix")
        self.assertIn("allowed", decision)
        self.assertIn("limit", decision)
        self.assertIn("remaining", decision)

    def test_limiter_blocks_once_budget_is_spent(self):
        # a small dedicated limiter with a frozen clock
        limiter = ratelimit.RateLimiter(limit=2, window_seconds=60, clock=lambda: 1000.0)
        self.assertTrue(limiter.check("k")["allowed"])
        self.assertTrue(limiter.check("k")["allowed"])
        third = limiter.check("k")
        self.assertFalse(third["allowed"])
        self.assertGreater(third["retry_after"], 0)

    def test_headers_include_standard_fields(self):
        h = ratelimit.headers({"limit": 120, "remaining": 5, "retry_after": 0})
        self.assertEqual(h["X-RateLimit-Limit"], "120")
        self.assertEqual(h["X-RateLimit-Remaining"], "5")
        self.assertIn("Retry-After", h)
