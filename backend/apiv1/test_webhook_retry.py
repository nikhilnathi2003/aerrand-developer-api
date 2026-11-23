from django.test import TestCase

from apiv1 import webhook_retry as wr


class WebhookRetryTests(TestCase):
    def test_exponential_backoff(self):
        self.assertEqual(wr.next_delay(1), 10)
        self.assertEqual(wr.next_delay(2), 20)
        self.assertEqual(wr.next_delay(3), 40)
        self.assertEqual(wr.next_delay(4), 80)

    def test_delay_is_capped(self):
        self.assertEqual(wr.next_delay(20), wr.MAX_DELAY_SECONDS)

    def test_stops_after_max_attempts(self):
        self.assertTrue(wr.should_retry(1))
        self.assertFalse(wr.should_retry(wr.MAX_ATTEMPTS))

    def test_no_retry_on_client_error_but_retry_on_server_error(self):
        self.assertFalse(wr.should_retry(1, status_code=404))   # 4xx — don't bother
        self.assertTrue(wr.should_retry(1, status_code=503))    # 5xx — try again

    def test_schedule_grows(self):
        s = wr.schedule()
        self.assertEqual(s[0], 10)
        self.assertTrue(all(s[i] <= s[i + 1] for i in range(len(s) - 1)))
