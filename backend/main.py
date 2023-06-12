from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
from backend.apis.base import api_router
from backend.core.config import settings
from backend.core.exceptions import ServiceException

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


@app.exception_handler(ServiceException)
async def service_exception_handler(request: Request, exc: ServiceException):
    """
    自定义告警，所以异常均抛出ServiceException错误，统一后端返回的数据格式
    """
    return JSONResponse(
        status_code=200,
        content={
            "success": False,
            "code": exc.code,
            "message": exc.message,
            "detail": exc.detail
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    覆盖默认的RequestValidationError，统一后端返回的数据格式
    """
    return JSONResponse(
        status_code=200,
        content={
            "success": False,
            "code": "ERR_001",
            "message": "数据验证错误",
            "detail": exc.errors(),
        }
    )

# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     raw_errors = exc.raw_errors
#     error_wrapper: ErrorWrapper = raw_errors[0]
#     pydantic_validation_error: ValidationError = error_wrapper.exc
#     validation_errors = pydantic_validation_error.errors()
#     first_error_msg = validation_errors[0]["msg"]
#
#     return JSONResponse(
#         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#         content={
#             "detail": validation_errors,
#             "reason": first_error_msg
#         }
#     )
