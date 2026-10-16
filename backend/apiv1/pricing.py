"""Server-side route pricing engine (the business engine).

The server always computes the price itself; POST /v1/errands takes a quote_id,
never a client-supplied price. These constants are our standalone approximation of
Aerrand's pricing engine (their exact constants live in their code and are an open
question to confirm). The breakdown fields match the Aerrand API contract.
"""
import math

HST_RATE = 0.13

# Tunable constants (approximate Aerrand's route engine; match the contract example).
STOP_BASE_FIRST = 6.00          # first stop
STOP_BASE_ADDITIONAL = 5.50     # each additional stop
DISTANCE_RATE_PER_KM = 0.869    # charged on routed km beyond the free allowance
FREE_KM = 0.0
SIZE_ADDON = {"small": 0.00, "medium": 2.00, "large": 4.00, "xl": 8.00}
CARGO_UNITS = {"small": 0.5, "medium": 1.0, "large": 2.0, "xl": 4.0}
INCLUDED_PARCELS_PER_STOP = 10
HANDLING_PER_EXTRA_PARCEL = 1.50
VAN_VOLUME_THRESHOLD = 15.0     # cargo units needing a van on volume alone
VOLUME_SURCHARGE_FLAT = 10.00
VAN_CAPACITY_CAP = 20.0         # above this, the route can't be booked


def haversine_km(a, b):
    """Great-circle distance in km between (lat, lng) points."""
    lat1, lng1 = float(a["lat"]), float(a["lng"])
    lat2, lng2 = float(b["lat"]), float(b["lng"])
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def route_km(pickup, stops):
    """Sum of sequential legs pickup -> stop1 -> ... -> stopN (haversine x1.3,
    the documented fallback when Google Distance Matrix isn't available)."""
    total = 0.0
    prev = pickup
    for s in stops:
        total += haversine_km(prev, s)
        prev = s
    return round(total * 1.3, 2)


def recommended_vehicle(units):
    if units <= 2:
        return "scooter"
    if units <= 5:
        return "motorcycle"
    if units <= 10:
        return "car"
    if units <= 20:
        return "van"
    return "truck"


def price_route(pickup, stops):
    """Compute the full priced breakdown for a route (1-5 stops).

    Each stop is a dict with a `parcels` dict like {"small": 2, "medium": 1}.
    Returns the breakdown in the contract's shape.
    """
    stop_count = len(stops)

    # parcel tallies
    total_parcels = 0
    size_addon = 0.0
    cargo_units = 0.0
    handling = 0.0
    for s in stops:
        parcels = s.get("parcels", {}) or {}
        stop_parcels = 0
        for size, qty in parcels.items():
            qty = int(qty)
            stop_parcels += qty
            size_addon += SIZE_ADDON.get(size, 0.0) * qty
            cargo_units += CARGO_UNITS.get(size, 1.0) * qty
        total_parcels += stop_parcels
        if stop_parcels > INCLUDED_PARCELS_PER_STOP:
            handling += (stop_parcels - INCLUDED_PARCELS_PER_STOP) * HANDLING_PER_EXTRA_PARCEL

    drop_base = STOP_BASE_FIRST + STOP_BASE_ADDITIONAL * (stop_count - 1)

    km = route_km(pickup, stops)
    distance_charge = max(0.0, km - FREE_KM) * DISTANCE_RATE_PER_KM

    requires_cargo = cargo_units > 10
    over_van = cargo_units > VAN_CAPACITY_CAP
    volume_surcharge = VOLUME_SURCHARGE_FLAT if cargo_units > VAN_VOLUME_THRESHOLD else 0.0

    route_price = drop_base + distance_charge + size_addon + handling + volume_surcharge
    route_price = round(route_price, 2)
    hst = round(route_price * HST_RATE, 2)
    charge_total = round(route_price + hst, 2)

    return {
        "currency": "CAD",
        "stopCount": stop_count,
        "totalParcels": total_parcels,
        "routeKm": km,
        "dropBaseTotal": round(drop_base, 2),
        "distanceCharge": round(distance_charge, 2),
        "sizeAddOnTotal": round(size_addon, 2),
        "handlingTotal": round(handling, 2),
        "volumeSurcharge": round(volume_surcharge, 2),
        "routePrice": route_price,
        "hstRate": HST_RATE,
        "hst": hst,
        "chargeTotal": charge_total,
        "amount_cents": round(charge_total * 100),
        "recommendedVehicle": recommended_vehicle(cargo_units),
        "requiresCargoVehicle": requires_cargo,
        "totalCargoUnits": round(cargo_units, 1),
        "overVanCapacity": over_van,
    }
