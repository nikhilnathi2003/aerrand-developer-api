"""Idempotency for create requests.

If a client retries POST /v1/errands with the same `Idempotency-Key`, we must not create a
second delivery. We store the first response keyed by (business, key); a replay returns that
stored response instead of booking again. The same key with a *different* body is a client
error (422), because the key no longer identifies the same request.
"""
import hashlib
import json
from datetime import datetime, timezone

from . import db


def _coll():
    return db.get_db()["idempotency_keys"]


def fingerprint(body) -> str:
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def lookup(owner, key):
    return _coll().find_one({"business_owner_id": owner, "key": key})


def save(owner, key, fp, response):
    _coll().insert_one({
        "business_owner_id": owner,
        "key": key,
        "fingerprint": fp,
        "response": response,
        "at": datetime.now(timezone.utc),
    })
