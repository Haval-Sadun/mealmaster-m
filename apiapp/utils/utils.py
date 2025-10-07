import logging
from ninja.responses import Response
from ..schemas.responses import APIError, APISuccess

logger = logging.getLogger(__name__)

def success(data, status_code: int = 200) -> Response:
    """Uniform success response"""
    return Response(APISuccess(status="success",data= data), status=status_code)

def error(message: str, status_code: int = 400, *, code: int | None = None, details=None, exc: Exception | None = None) -> Response:
    """Uniform error response with logging"""
    if exc:
        logger.exception("API Error: %s", message, exc_info=exc)
    else:
        logger.warning("API Warning: %s | Details: %s", message, details)

    return Response(APIError(message=message, code=code, details=details).dict(),status=status_code)