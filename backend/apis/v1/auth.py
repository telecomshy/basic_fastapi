import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Response, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from string import digits, ascii_letters
from uuid import UUID
from jose import jwt
from backend.schemas import schema_auth
from backend.db.crud import crud_user
from backend.core.dependencies import session_db
from backend.core.utils import verify_password, get_password_hash
from backend.core.exceptions import ServiceException
from backend.core.config import settings
from captcha.image import ImageCaptcha
from typing import Annotated

router = APIRouter()
uuid_captcha_mapping = {}


@router.post("/register", summary="用户注册", response_model=schema_auth.RegisterOut)
def register(register_data: schema_auth.RegisterIn, sess: Annotated[Session, Depends(session_db)]):
    """用户注册"""

    user_db = crud_user.get_user_by_username(sess, register_data.username)

    if user_db:
        raise ServiceException(code="ERR_002", message="用户已存在")

    try:
        hashed_password = get_password_hash(register_data.password1)
        user_id = crud_user.register_user(sess, register_data.username, hashed_password)
        return {"message": "用户ID", "data": user_id}
    except Exception:
        return ServiceException(code="ERR_007", message="注册失败")


@router.post("/login", summary="用户登陆", response_model=schema_auth.LoginOut)
def login(login_data: schema_auth.LoginIn, sess: Annotated[Session, Depends(session_db)]):
    """用户登陆，并添加验证码"""

    # 注意，uuid类型是UUID，所以要进行转换
    if login_data.captcha.lower() != uuid_captcha_mapping.get(str(login_data.uuid)):
        raise ServiceException(code="ERR_005", message="验证码错误")

    user_db = crud_user.get_user_by_username(sess, login_data.username)

    if user_db is None:
        raise ServiceException(code="ERR_003", message="用户名不存在")

    if not verify_password(login_data.password, user_db.password):
        raise ServiceException(code="ERR_004", message="密码不正确")

    if not user_db.active:
        raise ServiceException(code="ERR_009", message="用户已被锁定，请联系管理员!")

    # 创建token，过期时间添加到payload会自动生效，键值只能为exp
    access_token_expires = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"user_id": user_db.id, "exp": access_token_expires}
    access_token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    return {
        "message": "用户token",
        "data": {"token": access_token}
    }


@router.get("/captcha", summary="获取验证码", response_class=Response)
def get_captcha_image(uuid: UUID):
    """获取验证码"""

    captcha_text = ''.join(random.choices(ascii_letters + digits, k=4))
    captcha_text = captcha_text.lower()
    image = ImageCaptcha(height=38, width=100, font_sizes=(28, 30, 32))
    captcha_image = image.generate(captcha_text).getvalue()
    # 保存uuid和验证码的对应关系，登录的时候比较客户端输入的验证码与生成的验证码是否一致
    uuid_captcha_mapping.update({str(uuid): captcha_text})
    return Response(captcha_image, media_type="image/png")


@router.post("/login-openapi", summary="仅用于openAPI登录")
def login_openapi(
        db: Annotated[Session, Depends(session_db)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> dict:
    """仅用于fastapi openAPI文档的登录"""

    username, password = form_data.username, form_data.password
    user_db = crud_user.get_user_by_username(db, username)

    if user_db is None or not verify_password(password, user_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    payload = {"user_id": user_db.id}
    access_token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    # 返回json对象给前端，除了token，还包含前端需要的其它信息
    return {"access_token": access_token}
