from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """Liveness check that also reports whether MongoDB and Redis are reachable."""
    result = {"status": "ok", "service": "aerrand-developer-api", "version": "v1"}

    try:
        import pymongo

        client = pymongo.MongoClient(settings.MONGO_URL, serverSelectionTimeoutMS=1500)
        client.admin.command("ping")
        result["mongodb"] = "connected"
    except Exception as exc:  # noqa: BLE001 - report, don't crash the health check
        result["mongodb"] = f"unavailable ({exc.__class__.__name__})"

    try:
        import redis

        r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=1.5)
        r.ping()
        result["redis"] = "connected"
    except Exception as exc:  # noqa: BLE001
        result["redis"] = f"unavailable ({exc.__class__.__name__})"

    return Response(result)
