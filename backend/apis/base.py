from fastapi import APIRouter
from backend.apis.v1 import auth, user, report
from backend.core.config import settings


api_router = APIRouter()
api_router.include_router(auth.router, prefix=settings.base_url, tags=["auth"])
api_router.include_router(user.router, prefix=settings.base_url, tags=["user"])
api_router.include_router(report.router, prefix=settings.base_url, tags=["report"])
