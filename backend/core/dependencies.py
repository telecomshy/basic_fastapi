from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.db.base import SessionDB
from backend.core.config import settings
from backend.db.crud.users import get_user_by_username


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
            detail="Token过期或解析失败",
            headers={"WWW-Authenticate": "Bearer"}
        )


def get_current_user(db: Session = Depends(get_db), payload: dict = Depends(get_token_payload)):
    get_current_user_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法获取当前用户"
    )

    username = payload.get("sub")
    if username is None:
        raise get_current_user_error

    user_db = get_user_by_username(db, username=username)
    if user_db is None:
        raise get_current_user_error

    return user_db
