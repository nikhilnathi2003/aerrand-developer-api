"""API key authentication for /v1.

Reads `Authorization: Bearer ak_(test|live)_...`, hashes it, looks the hash up in
MongoDB, and rejects revoked/expired keys. On success it stamps the request with the
owning business id, the key's scopes, and its environment.
"""
from datetime import datetime, timezone

from rest_framework import authentication, exceptions

from . import db, keys


class ApiKeyError(exceptions.AuthenticationFailed):
    """Carries an error code so the view/handler can shape the response."""

    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


class ApiKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header:
            api_key = request.META.get("HTTP_X_API_KEY", "")
        elif header.startswith("Bearer "):
            api_key = header[len("Bearer "):].strip()
        else:
            raise ApiKeyError("invalid_api_key", "Authorization header must be 'Bearer <key>'.")

        if not api_key:
            raise ApiKeyError("invalid_api_key", "Missing API key.")

        if keys.environment_of(api_key) is None:
            raise ApiKeyError("invalid_api_key", "Malformed API key.")

        record = db.api_keys().find_one({"key_hash": keys.hash_key(api_key)})
        if not record:
            raise ApiKeyError("invalid_api_key", "Invalid API key.")
        if record.get("status") == "revoked":
            raise ApiKeyError("invalid_api_key", "This API key has been revoked.")

        expires_at = record.get("expires_at")
        if expires_at and _as_utc(expires_at) < datetime.now(timezone.utc):
            raise ApiKeyError("invalid_api_key", "This API key has expired.")

        # write-coalesced last-used stamp
        db.api_keys().update_one(
            {"_id": record["_id"]},
            {"$set": {"last_used_at": datetime.now(timezone.utc)}},
        )

        request.api_key = record  # business_owner_id, scopes, environment, ...
        return (_AnonBusiness(record["business_owner_id"]), record)


class _AnonBusiness:
    """Lightweight request.user standing in for the owning business."""

    is_authenticated = True

    def __init__(self, business_owner_id):
        self.business_owner_id = business_owner_id


def require_scope(request, scope):
    """Raise if the authenticating key lacks the given scope."""
    record = getattr(request, "api_key", None)
    if not record or scope not in record.get("scopes", []):
        raise ApiKeyError("insufficient_scope", f"This key is missing the '{scope}' scope.")


def _as_utc(dt):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
