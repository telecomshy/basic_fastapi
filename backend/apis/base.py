from fastapi import APIRouter
from .v1 import auth, user, report

api_router = APIRouter()

api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(user.router, tags=["user"])
api_router.include_router(report.router, tags=["report"])
