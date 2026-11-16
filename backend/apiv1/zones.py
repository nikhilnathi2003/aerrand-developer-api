"""Delivery-zone pre-check (Sujith — location/coverage).

Before a business bothers to build a quote, it can ask "do you actually deliver to this
spot?". This reuses the configured service areas and the same haversine distance math the
pricing engine uses, and reports whether a point is covered plus the nearest zone and how
far outside it falls — so the portal can warn "that's 3 km outside our Windsor zone"
instead of letting a booking fail later.
"""
from django.conf import settings

from . import pricing


def check(point):
    """Return coverage info for a {lat, lng} point.

    {
      "in_service_area": bool,
      "point": {...},
      "nearest": {"slug", "name", "distance_km", "radius_km", "km_outside"} | None,
    }
    """
    nearest = None
    for area in settings.SERVICE_AREAS:
        if not area.get("active"):
            continue
        dist = pricing.haversine_km(point, {"lat": area["lat"], "lng": area["lng"]})
        if nearest is None or dist < nearest["distance_km"]:
            nearest = {
                "slug": area["slug"],
                "name": area["name"],
                "distance_km": round(dist, 2),
                "radius_km": area["radius_km"],
                "km_outside": round(max(0.0, dist - area["radius_km"]), 2),
            }

    covered = bool(nearest and nearest["km_outside"] == 0)
    return {"in_service_area": covered, "point": point, "nearest": nearest}
