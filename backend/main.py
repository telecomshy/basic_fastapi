from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.apis.router_auth import router as user_router
from backend.core.config import settings

tags_metadata = [
    {
        "name": "auth",
        "description": "用户注册登陆接口"
    }
]

app = FastAPI(
    title="basic fastapi",
    description="基于fastapi的基础框架，包含用户注册认证，分权分域",
    version="0.0.1",
    openapi_tags=tags_metadata,
    contact={
        "name": "telecomshy",
        "email": "telecomshy@chinatelecom.cn"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(user_router)
