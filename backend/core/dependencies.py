from fastapi import Depends, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.db.base import SessionDB
from backend.db.crud.users import get_user_by_username, get_user_permissions
from backend.db.models.users import User, Permission

oauth2_scheme = OAuth2PasswordBearer('token')


def session():
    session_db = SessionDB()
    try:
        yield session_db
    finally:
        session_db.close()


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


def current_user(session_db: Session = Depends(session), payload: dict = Depends(token_payload)) -> User:
    get_current_user_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法获取当前用户"
    )

    username = payload.get("username")
    if username is None:
        raise get_current_user_error

    user_db = get_user_by_username(session_db, username=username)
    if user_db is None:
        raise get_current_user_error

    return user_db


def route_function_name(request: Request):
    """获取路径函数名称"""

    return request.scope['endpoint'].__name__


def user_permissions(user_db: User = Depends(current_user)):
    """获取当前用户权限"""

    return get_user_permissions(user_db)


def check_permission(
        func_name: str = Depends(route_function_name),
        user_perms: list[Permission] = Depends(user_permissions)
):
    """通过比较路径函数名称和用户权限来判断用户是否能调用路径函数"""

    perm_rules = [perm.perm_rule for perm in user_perms]
    if func_name not in perm_rules:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有相应的权限")
