"""Error responses in the Aerrand API contract's shape:

    { "error": { "code": "...", "message": "...", "details": {...} } }
"""
from rest_framework.response import Response


def error_response(code, message, status, details=None):
    body = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return Response(body, status=status)
