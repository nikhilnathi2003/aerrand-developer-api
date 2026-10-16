"""API key generation, hashing, and verification.

A key looks like:  ak_test_<40 base62 chars>  (or ak_live_...)
We store only a one-way hash: HMAC-SHA256(pepper, key). The plaintext key is shown
once at creation and never stored, so a database leak alone cannot verify keys.
"""
import hashlib
import hmac
import secrets

from django.conf import settings

_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
VALID_SCOPES = {"create", "read", "cancel"}


def _base62(nbytes: int) -> str:
    raw = secrets.token_bytes(nbytes)
    out = []
    n = int.from_bytes(raw, "big")
    while n > 0:
        n, rem = divmod(n, 62)
        out.append(_ALPHABET[rem])
    # pad to a stable length (~43 chars for 32 bytes)
    while len(out) < 40:
        out.append(_ALPHABET[secrets.randbelow(62)])
    return "".join(out[:40])


def generate_key(environment: str) -> str:
    """Return a fresh plaintext key, e.g. ak_test_xxxxxxxx…"""
    if environment not in ("test", "live"):
        raise ValueError("environment must be 'test' or 'live'")
    return f"ak_{environment}_{_base62(32)}"


def hash_key(key: str) -> str:
    """HMAC-SHA256 of the key, using the server-side pepper, as hex."""
    pepper = settings.API_KEY_HASH_PEPPER.encode()
    return hmac.new(pepper, key.encode(), hashlib.sha256).hexdigest()


def prefix_of(key: str) -> str:
    """Short display prefix stored for the dashboard, e.g. ak_test_A1B2C3."""
    return key[:14]


def environment_of(key: str) -> str | None:
    if key.startswith("ak_test_"):
        return "test"
    if key.startswith("ak_live_"):
        return "live"
    return None
