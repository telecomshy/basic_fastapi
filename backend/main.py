from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

# 覆盖默认的HTTPException，修改detail字段为reason字段，避免和pydantic数据验证失败422响应冲突，方便前端统一处理
# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"reason": exc.reason},
#         headers=exc.headers
#     )

# from pydantic.error_wrappers import ErrorWrapper
# from pydantic import ValidationError
# from fastapi.exceptions import RequestValidationError
# from fastapi import status

# 覆盖默认的RequestValidationError
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
