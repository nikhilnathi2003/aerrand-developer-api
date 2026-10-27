"""Driver position along the route — linear interpolation from pickup to drop-off.

The live tracking view uses this to place the driver on the map as a fraction of the way
from pickup to drop-off (0.0 = at pickup, 1.0 = arrived at the drop-off). Coordinates may
come in as strings or numbers, so they are coerced to float.
"""


def position_at(pickup, dropoff, fraction):
    """Point `fraction` of the way from pickup to dropoff (clamped to 0..1)."""
    f = max(0.0, min(1.0, float(fraction)))
    p_lat, p_lng = float(pickup["lat"]), float(pickup["lng"])
    d_lat, d_lng = float(dropoff["lat"]), float(dropoff["lng"])
    return {
        "lat": round(p_lat + (d_lat - p_lat) * f, 6),
        "lng": round(p_lng + (d_lng - p_lng) * f, 6),
    }
