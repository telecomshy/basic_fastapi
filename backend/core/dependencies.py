from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.db.base import SessionDB
from backend.db.crud.users import get_user_by_username
from backend.db.models.users import User

oauth2_scheme = OAuth2PasswordBearer('/api/v1/token')


def get_db():
    session = SessionDB()
    try:
        yield session
    finally:
        session.close()


def get_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        # 如果token解码失败，或者token过期，都会抛出错误，分别会抛出JWTClaimsError和ExpiredSignatureError错误
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token过期或解析失败",
            headers={"WWW-Authenticate": "Bearer"}
        )


def get_current_user(db: Session = Depends(get_db), payload: dict = Depends(get_token_payload)) -> User:
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

# class RequirePermissions:
#     def __init__(self, permissions: list[str]):
#         self.permissions = permissions
#
#     def __call__(self, user: User = Depends(get_current_user)) -> Never | None:
#         user_perms = get_user_permissions(user)
#
#         for perm in user_perms:
#             pass
