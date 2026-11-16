from django.test import TestCase

from apiv1 import webhooks


class WebhookVerifyTests(TestCase):
    def test_good_signature_passes(self):
        body = '{"hello":"world"}'
        sig = webhooks._sign(body)                     # the header we would send
        self.assertTrue(webhooks.verify_signature(body, sig))

    def test_tampered_body_fails(self):
        sig = webhooks._sign('{"hello":"world"}')
        self.assertFalse(webhooks.verify_signature('{"hello":"evil"}', sig))

    def test_wrong_secret_fails(self):
        body = '{"hello":"world"}'
        sig = webhooks._sign(body)
        self.assertFalse(webhooks.verify_signature(body, sig, secret="whsec_not_ours"))

    def test_malformed_header_fails(self):
        self.assertFalse(webhooks.verify_signature("{}", "not-a-sig"))
        self.assertFalse(webhooks.verify_signature("{}", ""))
