from fastapi import APIRouter
from .v1 import auth

api_router = APIRouter()

api_router.include_router(auth.router, tags=["auth"])
