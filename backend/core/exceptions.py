from typing import Any


class ServiceException(Exception):
    def __init__(self, code: str, message: str, detail: Any = None):
        self.code = code
        self.message = message
        self.detail = detail
