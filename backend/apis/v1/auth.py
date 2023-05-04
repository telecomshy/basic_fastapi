import random
from fastapi import APIRouter, Depends, Response, Form, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from captcha.image import ImageCaptcha
from passlib.context import CryptContext
from jose import jwt
from string import digits, ascii_letters
from datetime import timedelta, datetime
from uuid import UUID
from backend.schemas.users import UserRegister, UserFull
from backend.db.crud.users import get_user_by_username, create_user
from backend.core.config import settings
from backend.core.dependencies import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
uuid_captcha_mapping = {}


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(payload: dict, expires_delta: timedelta | None = None) -> str:
    payload = payload.copy()
    if expires_delta:
        expires = datetime.utcnow() + expires_delta
    else:
        expires = datetime.utcnow() + timedelta(minutes=15)
    payload.update({"exp": expires})
    access_token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return access_token


router = APIRouter()


@router.post("/register", summary="用户注册", response_model=UserFull)
def register(user: UserRegister, db: Session = Depends(get_db)):
    user_db = get_user_by_username(db, user.username)
    if user_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
    hashed_password = get_password_hash(user.password1)
    user_db = create_user(db, user.username, hashed_password)
    return user_db


@router.post("/login", summary="用户登陆")
def login(
        db: Session = Depends(get_db),
        username: str = Form(...),
        password: str = Form(...),
        uuid: str = Form(...),
        captcha: str = Form(...)
):
    user_db = get_user_by_username(db, username)

    if user_db is None or not verify_password(password, user_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    if captcha.lower() != uuid_captcha_mapping.get(uuid):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="验证码错误")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    # 将{"sub": username}编码成token，并添加过期时间
    access_token = create_access_token({"sub": username}, expires_delta=access_token_expires)
    # 返回json对象给前端，除了token，还包含前端需要的其它信息
    return {"access_token": access_token, "username": username}


@router.get("/captcha", summary="获取验证码", response_class=Response)
def get_captcha_image(uuid: UUID):
    captcha_text = ''.join(random.choices(ascii_letters + digits, k=4))
    captcha_text = captcha_text.lower()
    image = ImageCaptcha(height=38, width=100, font_sizes=(27, 29, 31))
    captcha_image = image.generate(captcha_text).getvalue()
    # 保存uuid和验证码的对应关系，登录的时候比较客户端输入的验证码与生成的验证码是否一致
    uuid_captcha_mapping.update({str(uuid): captcha_text})
    return Response(captcha_image, media_type="image/png")
