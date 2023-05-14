import random
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm
from captcha.image import ImageCaptcha
from string import digits, ascii_letters
from uuid import UUID
from jose import jwt
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Response, Form, status
from fastapi.exceptions import HTTPException
from backend.schemas.users import UserRegisterSche, UserInfoSche, PassUpdateSche, PermissionInfoSche
from backend.db.crud.users import get_user_by_username, create_user, update_user_password
from backend.db.models.users import User, Permission
from backend.core.dependencies import session, current_user, user_permissions
from backend.core.utils import verify_password, get_password_hash
from backend.core.config import settings

router = APIRouter()
uuid_captcha_mapping = {}


@router.post("/register", summary="用户注册", response_model=UserInfoSche)
def register(user_register_sche: UserRegisterSche, session_db: Session = Depends(session)):
    """用户注册"""

    user_db = get_user_by_username(session_db, user_register_sche.username)
    if user_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
    hashed_password = get_password_hash(user_register_sche.password1)
    user_db = create_user(session_db, user_register_sche.username, hashed_password)
    return user_db


def authenticate(session_db: Session, username: str, password: str) -> dict:
    user_db = get_user_by_username(session_db, username)

    if user_db is None or not verify_password(password, user_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    access_token_expires = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    # 过期时间添加了会自动生效
    payload = {"username": username, "exp": access_token_expires}
    access_token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    # 返回json对象给前端，除了token，还包含前端需要的其它信息
    return {"access_token": access_token, "username": username}


@router.post("/token", summary="仅用于openAPI登录")
def login_openapi(
        session_db: Session = Depends(session),
        login_form: OAuth2PasswordRequestForm = Depends()) -> dict:
    """用户fastapi openAPI授权登录"""

    response = authenticate(session_db, login_form.username, login_form.password)
    return response


@router.post("/login", summary="用户登陆")
def login(
        session_db: Session = Depends(session),
        login_form: OAuth2PasswordRequestForm = Depends(),
        uuid: str = Form(...),
        captcha: str = Form(...),
) -> dict:
    """用于普通客户端用户登陆，添加验证码"""

    if captcha.lower() != uuid_captcha_mapping.get(uuid):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="验证码错误")

    response = authenticate(session_db, login_form.username, login_form.password)
    return response


@router.get("/captcha", summary="获取验证码", response_class=Response)
def get_captcha_image(uuid: UUID):
    """获取验证码"""

    captcha_text = ''.join(random.choices(ascii_letters + digits, k=4))
    captcha_text = captcha_text.lower()
    image = ImageCaptcha(height=38, width=100, font_sizes=(27, 29, 31))
    captcha_image = image.generate(captcha_text).getvalue()
    # 保存uuid和验证码的对应关系，登录的时候比较客户端输入的验证码与生成的验证码是否一致
    uuid_captcha_mapping.update({str(uuid): captcha_text})
    return Response(captcha_image, media_type="image/png")


@router.post("/update-pass", summary="修改密码", response_model=UserInfoSche)
def update_password(pass_update_sche: PassUpdateSche, db: Session = Depends(session),
                    user_db: User = Depends(current_user)):
    """更新用户密码"""

    # 先检查原始密码是否正确
    if not verify_password(pass_update_sche.old_password, user_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="原始密码错误")

    hashed_password = get_password_hash(pass_update_sche.new_password1)
    user_db = update_user_password(db=db, user=user_db, hashed_password=hashed_password)
    return user_db


@router.get("/user-perms", summary="获取当前用户权限", response_model=list[PermissionInfoSche])
def get_user_permissions(user_permissions_db: list[Permission] = Depends(user_permissions)):
    """根据用户角色获取相应的菜单"""

    return user_permissions_db
