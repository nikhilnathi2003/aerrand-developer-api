"""Per-key request rate limiting (fixed window).

Each API key gets a budget of N requests per time window. We keep a small counter per key
and window; once the budget is used up we return a retry-after so the caller can back off
and hit 429 instead of overloading the service. The clock is injectable so the behaviour
is easy to test. In production the counter lives in Redis (shared across processes);
wiring this into the request path and adding the Redis backend is the next step.
"""
import time


class RateLimiter:
    def __init__(self, limit, window_seconds, clock=time.time):
        self.limit = int(limit)
        self.window = int(window_seconds)
        self.clock = clock
        self._hits = {}  # key -> (window_start, count)

    def check(self, key):
        """Count one request for `key` and return the limit decision."""
        now = self.clock()
        start, count = self._hits.get(key, (now, 0))
        if now - start >= self.window:
            start, count = now, 0
        count += 1
        self._hits[key] = (start, count)
        allowed = count <= self.limit
        reset_in = max(0, int(self.window - (now - start)))
        return {
            "allowed": allowed,
            "limit": self.limit,
            "remaining": max(0, self.limit - count),
            "retry_after": 0 if allowed else reset_in,
        }
