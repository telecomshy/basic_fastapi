from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .database import ProdSession
from .config import settings
from .exceptions import credentials_exception
from .user.crud import get_user_by_username


def get_db():
    session = ProdSession()
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
        raise credentials_exception


def get_current_user(db: Session = Depends(get_db), payload: dict = Depends(get_token_payload)):
    username = payload.get("sub")
    if username is None:
        raise credentials_exception
    user_db = get_user_by_username(db, username=username)
    if user_db is None:
        raise credentials_exception
    return user_db
