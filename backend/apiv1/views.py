import secrets
import uuid
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.shortcuts import render
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from . import db, keys, pricing
from .authentication import ApiKeyAuthentication, require_scope
from .errors import error_response

_KEY_NS = uuid.UUID("a1b2c3d4-0000-4000-8000-000000000000")

_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no ambiguous chars


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _now():
    return datetime.now(timezone.utc)


def _delivery_code():
    return "".join(secrets.choice(_CODE_ALPHABET) for _ in range(6))


def _in_service_area(point):
    for area in settings.SERVICE_AREAS:
        if not area.get("active"):
            continue
        d = pricing.haversine_km(point, {"lat": area["lat"], "lng": area["lng"]})
        if d <= area["radius_km"]:
            return True
    return False


def _valid_point(obj):
    try:
        float(obj["lat"]), float(obj["lng"])
        return True
    except (KeyError, TypeError, ValueError):
        return False


# --------------------------------------------------------------------------- #
# health (no auth)
# --------------------------------------------------------------------------- #
@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    result = {"status": "ok", "service": "aerrand-developer-api", "version": "v1"}
    try:
        import pymongo

        pymongo.MongoClient(settings.MONGO_URL, serverSelectionTimeoutMS=1500).admin.command("ping")
        result["mongodb"] = "connected"
    except Exception as exc:  # noqa: BLE001
        result["mongodb"] = f"unavailable ({exc.__class__.__name__})"
    try:
        import redis

        redis.from_url(settings.REDIS_URL, socket_connect_timeout=1.5).ping()
        result["redis"] = "connected"
    except Exception as exc:  # noqa: BLE001
        result["redis"] = f"unavailable ({exc.__class__.__name__})"
    return Response(result)


# --------------------------------------------------------------------------- #
# GET /v1/service-areas
# --------------------------------------------------------------------------- #
@api_view(["GET"])
@permission_classes([AllowAny])
def service_areas(request):
    areas = [
        {"slug": a["slug"], "name": a["name"], "province": a["province"],
         "lat": a["lat"], "lng": a["lng"], "radiusKm": a["radius_km"], "active": a["active"]}
        for a in settings.SERVICE_AREAS
    ]
    return Response({"serviceAreas": areas, "updatedAt": _now().isoformat()})


# --------------------------------------------------------------------------- #
# POST /v1/quotes  — route quote
# --------------------------------------------------------------------------- #
@api_view(["POST"])
@authentication_classes([ApiKeyAuthentication])
@permission_classes([IsAuthenticated])
def quotes(request):
    require_scope(request, "read")
    body = request.data or {}

    pickup = body.get("pickup")
    stops = body.get("stops")
    # allow a single drop-off phrased as dropoff
    if stops is None and body.get("dropoff") is not None:
        stops = [body["dropoff"]]

    details = {}
    if not isinstance(pickup, dict) or not _valid_point(pickup):
        details["pickup"] = "pickup with numeric lat/lng is required"
    if not isinstance(stops, list) or not (1 <= len(stops) <= 5):
        details["stops"] = "1 to 5 stops are required"
    if details:
        return error_response("validation_failed", "Invalid request.", 400, details)

    for i, s in enumerate(stops):
        if not _valid_point(s):
            return error_response("validation_failed", "Invalid request.", 400,
                                  {f"stops[{i}]": "numeric lat/lng required"})

    # service-area check
    outside = []
    for i, p in enumerate([pickup, *stops]):
        if not _in_service_area(p):
            outside.append(i)
    if outside:
        return error_response(
            "service_area_unavailable",
            "A pickup or drop-off is outside a served city.",
            412,
            {"outside_indexes": outside},
        )

    breakdown = pricing.price_route(pickup, stops)
    if breakdown["overVanCapacity"]:
        return error_response("route_over_capacity",
                              "Route exceeds one cargo van; split the booking.", 400)

    quote_id = "qt_" + uuid.uuid4().hex[:22]
    expires_at = _now() + timedelta(seconds=settings.API_QUOTE_TTL_SECONDS)
    db.quotes().insert_one({
        "quote_id": quote_id,
        "business_owner_id": request.user.business_owner_id,
        "environment": request.api_key["environment"],
        "pickup": pickup,
        "stops": stops,
        "breakdown": breakdown,
        "expires_at": expires_at,
        "created_at": _now(),
    })

    return Response({"quote_id": quote_id, "expires_at": expires_at.isoformat(), **breakdown})


# --------------------------------------------------------------------------- #
# POST /v1/errands  — create a (test-mode) delivery, priced from the quote
# --------------------------------------------------------------------------- #
@api_view(["GET", "POST"])
@authentication_classes([ApiKeyAuthentication])
@permission_classes([IsAuthenticated])
def errands_collection(request):
    """GET lists the business's errands; POST creates one."""
    if request.method == "GET":
        return _list_errands(request)
    return _create_errand(request)


def _create_errand(request):
    require_scope(request, "create")
    body = request.data or {}
    owner = request.user.business_owner_id
    environment = request.api_key["environment"]

    quote_id = body.get("quote_id")
    if not quote_id:
        return error_response("validation_failed", "Invalid request.", 400,
                              {"quote_id": "quote_id is required (price is server-computed)"})

    quote = db.quotes().find_one({"quote_id": quote_id, "business_owner_id": owner})
    if not quote:
        return error_response("errand_not_found", "Quote not found.", 404)
    exp = quote["expires_at"]
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if exp < _now():
        return error_response("quote_expired", "Quote has expired; request a new one.", 409)

    # drop-offs: dropoffs[] (multi) or dropoff (single)
    dropoffs = body.get("dropoffs")
    if dropoffs is None and body.get("dropoff") is not None:
        dropoffs = [body["dropoff"]]
    if not isinstance(dropoffs, list) or not (1 <= len(dropoffs) <= 5):
        return error_response("validation_failed", "Invalid request.", 400,
                              {"dropoffs": "1 to 5 drop-offs required"})

    pickup = body.get("pickup") or quote["pickup"]
    if not _valid_point(pickup):
        return error_response("validation_failed", "Invalid request.", 400,
                              {"pickup": "numeric lat/lng required"})
    for i, d in enumerate(dropoffs):
        if not _valid_point(d):
            return error_response("validation_failed", "Invalid request.", 400,
                                  {f"dropoffs[{i}]": "numeric lat/lng required"})
        contact = d.get("contact") or {}
        if not contact.get("name") or not contact.get("phone_number"):
            return error_response("validation_failed", "Invalid request.", 400,
                                  {f"dropoffs[{i}].contact": "name and phone_number required"})

    breakdown = quote["breakdown"]
    charge_total = breakdown["chargeTotal"]
    is_test = environment == "test"
    batch_id = uuid.uuid4().hex if len(dropoffs) > 1 else None

    # split the price across stops; reconcile the remainder on the last stop
    n = len(dropoffs)
    per_stop = round(charge_total / n, 2)
    stop_prices = [per_stop] * n
    stop_prices[-1] = round(charge_total - per_stop * (n - 1), 2)

    created = []
    for index, d in enumerate(dropoffs):
        errand_id = str(uuid.uuid4())
        doc = {
            "errand_id": errand_id,
            "business_owner_id": owner,
            "environment": environment,
            "test_mode": is_test,
            "status": "pending_payment",
            "reference": d.get("reference") or body.get("reference"),
            "batch_id": batch_id,
            "batch_index": index if batch_id else None,
            "pickup": pickup,
            "dropoff": d,
            "vehicle_type": body.get("vehicle_type") or breakdown["recommendedVehicle"],
            "scheduled_at": body.get("scheduled_at"),
            "delivery_code": _delivery_code(),
            "price": stop_prices[index],
            "pricing": breakdown,
            "payment": {"status": "unpaid", "method": (body.get("payment") or {}).get("method", "wallet")},
            "metadata": body.get("metadata") or {},
            "created_at": _now(),
        }
        db.errands().insert_one(doc)
        created.append(doc)

    if batch_id:
        return Response(_batch_response(created, breakdown, batch_id), status=201)
    return Response(_errand_response(created[0]), status=201)


# --------------------------------------------------------------------------- #
# GET /v1/errands/{id}
# --------------------------------------------------------------------------- #
@api_view(["GET"])
@authentication_classes([ApiKeyAuthentication])
@permission_classes([IsAuthenticated])
def get_errand(request, errand_id):
    require_scope(request, "read")
    owner = request.user.business_owner_id
    # tenant isolation: scope every lookup to the owning business
    doc = db.errands().find_one({"errand_id": errand_id, "business_owner_id": owner})
    if not doc:
        return error_response("errand_not_found", "Errand not found.", 404)
    return Response(_errand_response(doc))


# --------------------------------------------------------------------------- #
# response shapers
# --------------------------------------------------------------------------- #
def _errand_response(doc):
    b = doc["pricing"]
    return {
        "errand_id": doc["errand_id"],
        "status": doc["status"],
        "test_mode": doc["test_mode"],
        "reference": doc.get("reference"),
        "batch_id": doc.get("batch_id"),
        "delivery_code": doc["delivery_code"],
        "vehicle_type": doc["vehicle_type"],
        "scheduled_at": doc.get("scheduled_at"),
        "pickup": doc["pickup"],
        "dropoff": doc["dropoff"],
        "pricing": {
            "currency": b["currency"],
            "route_price": b["routePrice"],
            "hst": b["hst"],
            "charge_total": b["chargeTotal"],
            "price_for_this_stop": doc["price"],
        },
        "payment": doc["payment"],
        "metadata": doc.get("metadata", {}),
        "created_at": doc["created_at"].isoformat(),
    }


def _batch_response(docs, breakdown, batch_id):
    return {
        "batch_id": batch_id,
        "status": "pending_payment",
        "stop_count": len(docs),
        "test_mode": docs[0]["test_mode"],
        "created_at": docs[0]["created_at"].isoformat(),
        "pricing": {
            "currency": breakdown["currency"],
            "route_price": breakdown["routePrice"],
            "hst": breakdown["hst"],
            "charge_total": breakdown["chargeTotal"],
        },
        "stops": [
            {
                "errand_id": d["errand_id"],
                "index": d["batch_index"],
                "reference": d.get("reference"),
                "status": d["status"],
                "price": d["price"],
                "delivery_code": d["delivery_code"],
            }
            for d in docs
        ],
    }


# --------------------------------------------------------------------------- #
# Developer dashboard (web UI) + helpers it needs
# --------------------------------------------------------------------------- #
def dashboard(request):
    """Serve the developer dashboard page."""
    return render(request, "dashboard.html")


@api_view(["POST"])
@permission_classes([AllowAny])
def create_test_key(request):
    """Dashboard key creation — TEST keys only (live keys are issued by command)."""
    body = request.data or {}
    business = (body.get("business") or "Demo Business").strip()
    owner_id = str(uuid.uuid5(_KEY_NS, business.lower()))
    plaintext = keys.generate_key("test")
    db.api_keys().insert_one({
        "id": str(uuid.uuid4()),
        "business_owner_id": owner_id,
        "business_name": business,
        "name": "dashboard",
        "environment": "test",
        "key_prefix": keys.prefix_of(plaintext),
        "key_hash": keys.hash_key(plaintext),
        "scopes": ["create", "read", "cancel"],
        "status": "active",
        "expires_at": None,
        "created_at": _now(),
        "last_used_at": None,
    })
    return Response({"key": plaintext, "prefix": keys.prefix_of(plaintext),
                     "business": business, "environment": "test",
                     "scopes": ["create", "read", "cancel"]}, status=201)


@api_view(["POST"])
@permission_classes([AllowAny])
def revoke_test_key(request):
    """Revoke a key from the dashboard (demo). Revocation is immediate and irreversible."""
    prefix = (request.data or {}).get("prefix")
    if not prefix:
        return error_response("validation_failed", "prefix is required", 400)
    result = db.api_keys().update_one(
        {"key_prefix": prefix, "status": {"$ne": "revoked"}},
        {"$set": {"status": "revoked", "revoked_at": _now()}},
    )
    if result.matched_count == 0:
        return error_response("errand_not_found", "No active key with that prefix.", 404)
    return Response({"status": "revoked", "prefix": prefix})


def _list_errands(request):
    require_scope(request, "read")
    owner = request.user.business_owner_id
    docs = list(db.errands().find({"business_owner_id": owner}).sort("created_at", -1).limit(20))
    return Response({"errands": [_errand_response(d) for d in docs]})
