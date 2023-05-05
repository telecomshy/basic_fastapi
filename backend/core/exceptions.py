from typing import Any


class HTTPException(Exception):
    def __init__(self, status_code: int, reason: Any, headers: dict[str, Any] | None = None):
        self.status_code = status_code
        self.reason = reason
        self.headers = headers
