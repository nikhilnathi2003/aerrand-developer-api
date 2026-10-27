"""ETA helper for live tracking — rough minutes from the driver to the drop-off."""
import math


def _km(a, b):
    r = 6371.0
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dp = math.radians(b["lat"] - a["lat"])
    dl = math.radians(b["lng"] - a["lng"])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def estimate_minutes(driver, dropoff, kmph=24.0):
    km = _km(driver, dropoff) * 1.3
    return max(1, round(km / (kmph / 60)))
