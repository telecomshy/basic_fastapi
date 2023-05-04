from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from backend.apis.base import api_router
from backend.core.config import settings

tags_metadata = [
    {
        "name": "auth",
        "description": "用户注册登陆"
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

app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(exc.errors())
    print(exc.raw_errors)

    error_wrapper = exc.raw_errors[0]
    pydantic_validation_error = error_wrapper.exc
    print(type(pydantic_validation_error))
    print(pydantic_validation_error)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )
