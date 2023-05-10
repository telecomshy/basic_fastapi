from datetime import datetime, timedelta
from typing import TypeVar
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.core.utils import verify_password
from backend.core.exceptions import HTTPException
from backend.db.base import SessionDB
from backend.db.crud.users import get_user_by_username, get_user_permissions
from backend.db.models.users import User, Role, Menu


def get_db():
    session = SessionDB()
    try:
        yield session
    finally:
        session.close()


oauth2_scheme = OAuth2PasswordBearer('login')


def get_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        # 如果token解码失败，或者token过期，都会抛出错误，分别会抛出JWTClaimsError和ExpiredSignatureError错误
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            reason="Token过期或解析失败",
            headers={"WWW-Authenticate": "Bearer"}
        )


def authenticate_user(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> dict:
    """登录认证"""

    username, password = form_data.username, form_data.password
    user_db = get_user_by_username(db, username)

    if user_db is None or not verify_password(password, user_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, reason="用户名或密码错误")

    access_token_expires = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    # 过期时间添加了会自动生效
    payload = {"username": username, "exp": access_token_expires}
    access_token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    # 返回json对象给前端，除了token，还包含前端需要的其它信息
    return {"access_token": access_token, "username": username}


def get_current_user(db: Session = Depends(get_db), payload: dict = Depends(get_token_payload)) -> User:
    get_current_user_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        reason="无法获取当前用户"
    )

    username = payload.get("username")
    if username is None:
        raise get_current_user_error

    user_db = get_user_by_username(db, username=username)
    if user_db is None:
        raise get_current_user_error

    return user_db


def get_current_user_menu(user_db: Depends(get_current_user)) -> list[Menu]:
    """获取当前用户的菜单"""

    menus = set()
    roles = user_db.roles
    for role in roles:
        for menu in role.menus:
            menus.add(menu)
    return list(menus)

# class RequirePermissions:
#     def __init__(self, permissions: list[str]):
#         self.permissions = permissions
#
#     def __call__(self, user: User = Depends(get_current_user)) -> Never | None:
#         user_perms = get_user_permissions(user)
#
#         for perm in user_perms:
#             pass
