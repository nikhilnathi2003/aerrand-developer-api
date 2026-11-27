"""Webhook retry schedule (Charan) — backoff for failed webhook deliveries.

When pushing an event to a partner's URL fails, we don't give up right away — we retry
with exponential backoff (delays that grow each time) up to a maximum number of attempts.
This is the pure scheduling logic the dispatcher uses: how long to wait before each retry,
and when to stop. It covers the "real webhook retries" next-step on our board.
"""
BASE_DELAY_SECONDS = 10
MAX_DELAY_SECONDS = 3600      # never wait longer than an hour between tries
MAX_ATTEMPTS = 6


def next_delay(attempt, base=BASE_DELAY_SECONDS, cap=MAX_DELAY_SECONDS):
    """Seconds to wait before retry number ``attempt`` (1-based): 10, 20, 40, 80 … capped."""
    if attempt < 1:
        return 0
    return min(cap, base * (2 ** (attempt - 1)))


def should_retry(attempt, status_code=None, max_attempts=MAX_ATTEMPTS):
    """Whether to try again after ``attempt`` failed attempts.

    Stop once we hit ``max_attempts``. Also stop on a 4xx response — a client error means
    retrying the same request won't help. Keep retrying on network errors or 5xx.
    """
    if attempt >= max_attempts:
        return False
    if status_code is not None and 400 <= status_code < 500:
        return False
    return True


def schedule(max_attempts=MAX_ATTEMPTS):
    """The full list of backoff delays before each retry — handy for display and testing."""
    return [next_delay(a) for a in range(1, max_attempts)]
