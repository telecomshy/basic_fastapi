from datetime import datetime, timedelta
from fastapi import Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.core.utils import verify_password
from backend.db.base import SessionDB
from backend.db.crud.users import get_user_by_username, get_user_permissions
from backend.db.models.users import User

oauth2_scheme = OAuth2PasswordBearer('token')


def session():
    session_db = SessionDB()
    try:
        yield session_db
    finally:
        session_db.close()


def authenticate_user(
        db: Session = Depends(session),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> dict:
    """登录认证"""

    username, password = form_data.username, form_data.password
    user_db = get_user_by_username(db, username)

    if user_db is None or not verify_password(password, user_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    access_token_expires = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    # 过期时间添加了会自动生效
    payload = {"username": username, "exp": access_token_expires}
    access_token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    # 返回json对象给前端，除了token，还包含前端需要的其它信息
    return {"access_token": access_token, "username": username}


def token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        # 如果token解码失败，或者token过期，都会抛出错误，分别会抛出JWTClaimsError和ExpiredSignatureError错误
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token过期或解析失败",
            headers={"WWW-Authenticate": "Bearer"}
        )


def current_user(db: Session = Depends(session), payload: dict = Depends(token_payload)) -> User:
    get_current_user_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法获取当前用户"
    )

    username = payload.get("username")
    if username is None:
        raise get_current_user_error

    user_db = get_user_by_username(db, username=username)
    if user_db is None:
        raise get_current_user_error

    return user_db


def route_function_name(request: Request):
    return request.scope['endpoint'].__name__


def check_permission(
        func_name: str = Depends(route_function_name),
        user_db: User = Depends(current_user)
):
    perm_rules = [perm.perm_rule for perm in get_user_permissions(user_db)]
    if func_name not in perm_rules:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有相应的权限")
