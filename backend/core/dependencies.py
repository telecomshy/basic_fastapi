from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.core.exceptions import ServiceException
from backend.core.utils import convert_to_list
from backend.db.base import SessionDB
from backend.db.crud.user import get_user_db_by_id, get_user_db_permissions
from backend.db.models.user import User
from typing import Annotated


def session_db():
    session = SessionDB()
    try:
        yield session
    finally:
        session.close()


class Authorization(OAuth2PasswordBearer):
    """覆盖默认的OAuth，以同时支持openapi文档的认证以及前端认证"""

    async def __call__(self, request: Request):
        scheme_token_str = request.headers.get("Authorization")
        scheme, token_str = get_authorization_scheme_param(scheme_token_str)
        try:
            # 如果token解码失败，或者token过期，都会抛出错误，分别会抛出JWTClaimsError和ExpiredSignatureError错误
            return jwt.decode(token_str, settings.secret_key, algorithms=[settings.algorithm])
        except (JWTError, KeyError):
            raise ServiceException(code="ERR_006", message="token过期或解析失败")


authorization = Authorization(f"{settings.base_url}/login-openapi")


def current_user(
        sess: Annotated[Session, Depends(session_db)],
        payload: Annotated[dict, Depends(authorization)]
) -> User:
    """获取当前用户"""

    user_id = payload.get("user_id")
    return get_user_db_by_id(sess, user_id)


class RequiredPermissions:
    def __init__(self, *args):
        self.required_perms = convert_to_list(*args)

    def __call__(self, user=Depends(current_user)):
        user_perms = [perm.perm_rule for perm in get_user_db_permissions(user)]
        if any(required_perm not in user_perms for required_perm in self.required_perms):
            raise ServiceException(code="ERR_008", message="无相应权限")
