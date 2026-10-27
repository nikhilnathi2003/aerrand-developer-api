"""Turn a typed address or place name into coordinates (geocoding).

Known Windsor places resolve instantly from a small built-in table (works offline,
no network). Anything else is looked up through OpenStreetMap's free Nominatim
service, biased to the Windsor area. Returns None when it can't be resolved.
"""
import json
import urllib.parse
import urllib.request

# Known places resolve immediately, no network call needed.
PRESETS = {
    "downtown windsor": (42.3149, -83.0364),
    "university of windsor": (42.3060, -83.0665),
    "devonshire mall": (42.2606, -82.9962),
    "windsor airport": (42.2756, -82.9556),
    "st clair college": (42.2342, -83.0699),
    "riverside": (42.3300, -82.9400),
    "tecumseh": (42.3100, -82.8960),
    "lasalle": (42.2200, -83.0700),
}

# Bounding box around Windsor (left,top,right,bottom as lng,lat) to bias lookups.
_VIEWBOX = "-83.15,42.40,-82.85,42.20"


def geocode(query):
    """Return {'lat', 'lng', 'label'} for an address/place, or None if not found."""
    if not query or not query.strip():
        return None
    q = query.strip()
    key = q.lower().replace(".", "").replace(",", " ")
    key = " ".join(key.split())
    for name, (lat, lng) in PRESETS.items():
        if name in key:
            return {"lat": lat, "lng": lng, "label": q}
    # fall back to OpenStreetMap Nominatim (free, no API key)
    try:
        params = urllib.parse.urlencode({
            "q": q + ", Windsor, Ontario, Canada",
            "format": "json", "limit": "1",
            "viewbox": _VIEWBOX, "bounded": "1",
        })
        url = "https://nominatim.openstreetmap.org/search?" + params
        req = urllib.request.Request(url, headers={"User-Agent": "aerrand-dev-portal/1.0"})
        with urllib.request.urlopen(req, timeout=4) as r:
            data = json.loads(r.read())
        if data:
            return {"lat": float(data[0]["lat"]), "lng": float(data[0]["lon"]), "label": q}
    except Exception:
        return None
    return None
