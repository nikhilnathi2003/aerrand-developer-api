"""DRF exception handler that renders errors in the Aerrand contract's shape."""
from rest_framework.views import exception_handler as drf_exception_handler

from .authentication import ApiKeyError
from .errors import error_response

_STATUS_FOR_CODE = {
    "invalid_api_key": 401,
    "insufficient_scope": 403,
}


def custom_exception_handler(exc, context):
    if isinstance(exc, ApiKeyError):
        status = _STATUS_FOR_CODE.get(exc.code, 401)
        return error_response(exc.code, str(exc.detail), status)
    return drf_exception_handler(exc, context)
