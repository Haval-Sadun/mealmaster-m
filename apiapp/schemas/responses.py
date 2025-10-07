from ninja import Schema
from typing import Optional, Any

class APIError(Schema):
    status: str = "error"
    message: str
    code: Optional[int] = None
    details: Optional[Any] = None

class APISuccess(Schema):
    status: str = "success"
    data: Any
