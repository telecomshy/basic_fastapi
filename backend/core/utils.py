from passlib.context import CryptContext

from fastapi import Response, Request
from fastapi.routing import APIRoute
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Callable
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


class NormalizedResponseRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            response: Response = await original_route_handler(request)
            if "json" in response.media_type:
                result = json.loads(response.body)
                response.body = json.dumps({"data": result}).encode("utf8")
            return response

        return custom_route_handler
