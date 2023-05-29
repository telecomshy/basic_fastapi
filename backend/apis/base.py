from fastapi import APIRouter
from .v1 import security, user, report

api_router = APIRouter()

api_router.include_router(security.router, prefix="/api/v1", tags=["auth"])
api_router.include_router(user.router, prefix="/api/v1", tags=["user"])
api_router.include_router(report.router, prefix="/api/v1", tags=["report"])
