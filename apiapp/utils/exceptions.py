import logging
from ninja.responses import Response
from ..schemas.responses import APIError

logger = logging.getLogger("django")

def global_exception_handler(request, exc):
    """
    Catch any uncaught exception from Ninja routes and return a clean JSON error.
    """
    logger.exception("Unhandled exception in API", exc_info=exc)

    payload = APIError(message="Internal server error", code=500, details=None ).dict()

    return Response(payload, status=500)
