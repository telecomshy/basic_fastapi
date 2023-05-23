from fastapi import APIRouter
from .v1 import auth, user, report

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/api/v1", tags=["auth"])
api_router.include_router(user.router, prefix="/api/v1", tags=["user"])
api_router.include_router(report.router, prefix="/api/v1", tags=["report"])
