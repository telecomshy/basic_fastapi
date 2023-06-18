from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.core.exceptions import ServiceException
from backend.db.base import SessionDB
from backend.db.crud.user import get_user_by_id
from backend.db.models.user import User


def session_db():
    session = SessionDB()
    try:
        yield session
    finally:
        session.close()


class Authorization(OAuth2PasswordBearer):
    """覆盖默认的OAuth"""
    async def __call__(self, request: Request):
        scheme_token_str = request.headers.get("Authorization")
        scheme, token_str = get_authorization_scheme_param(scheme_token_str)
        try:
            # 如果token解码失败，或者token过期，都会抛出错误，分别会抛出JWTClaimsError和ExpiredSignatureError错误
            return jwt.decode(token_str, settings.secret_key, algorithms=[settings.algorithm])
        except (JWTError, KeyError):
            raise ServiceException(code="ERR_006", message="token过期或解析失败")


authorization = Authorization(f"{settings.base_url}/login-openapi")


def current_user(sess: Session = Depends(session_db), payload: dict = Depends(authorization)) -> User:
    """获取当前用户"""

    user_id = payload.get("user_id")
    return get_user_by_id(sess, user_id)
