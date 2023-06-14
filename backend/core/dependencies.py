from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.core.exceptions import ServiceException
from backend.db.base import SessionDB
from backend.db.crud.user import get_user_by_id
from backend.db.models.user import User

oauth2_scheme = OAuth2PasswordBearer('/api/v1/token')


def session_db():
    session = SessionDB()
    try:
        yield session
    finally:
        session.close()


def authorization(request: Request) -> dict:
    try:
        # openAPI返回的Authorization header头前面总是有Bearer，自定义的可能没有scheme_name，所以切分获取实际的token
        token = request.headers["Authorization"].split()[-1]
        # 如果token解码失败，或者token过期，都会抛出错误，分别会抛出JWTClaimsError和ExpiredSignatureError错误
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except (JWTError, KeyError):
        raise ServiceException(code="ERR_006", message="token过期或解析失败")


def current_user(sess: Session = Depends(session_db), payload: dict = Depends(authorization)) -> User:
    """获取当前用户"""

    user_id = payload.get("user_id")
    return get_user_by_id(sess, user_id)
