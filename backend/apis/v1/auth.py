import random
from typing import TypeVar
from fastapi import APIRouter, Depends, Response, Form, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from captcha.image import ImageCaptcha
from string import digits, ascii_letters
from uuid import UUID
from backend.schemas.users import UserRegisterSche, UserInfoSche, PassUpdateSche
from backend.db.crud.users import get_user_by_username, create_user, update_user_password
from backend.db.models.users import User
from backend.core.dependencies import get_db, get_current_user, authenticate_user
from backend.core.utils import verify_password, get_password_hash

router = APIRouter()
uuid_captcha_mapping = {}


@router.post("/register", summary="用户注册", response_model=UserInfoSche)
def register(user_register_sche: UserRegisterSche, db: Session = Depends(get_db)):
    """用户注册"""

    user_db = get_user_by_username(db, user_register_sche.username)
    if user_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
    hashed_password = get_password_hash(user_register_sche.password1)
    user_db = create_user(db, user_register_sche.username, hashed_password)
    return user_db


LoginResponse = TypeVar("LoginResponse", bound=dict)


@router.post("/token", summary="仅用于openAPI登录")
def login_openapi(login_response: LoginResponse = Depends(authenticate_user)) -> LoginResponse:
    """用户fastapi openAPI授权登录"""

    return login_response


@router.post("/login", summary="用户登陆")
def login(
        uuid: str = Form(...),
        captcha: str = Form(...),
        login_response: LoginResponse = Depends(authenticate_user)
) -> LoginResponse:
    """用于普通客户端用户登陆，并添加验证码"""

    if captcha.lower() != uuid_captcha_mapping.get(uuid):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="验证码错误")

    return login_response


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
def update_password(pass_update_sche: PassUpdateSche, db: Session = Depends(get_db),
                    user_db: User = Depends(get_current_user)):
    """更新用户密码"""

    # 先检查原始密码是否正确
    if not verify_password(pass_update_sche.old_password, user_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="原始密码错误")

    hashed_password = get_password_hash(pass_update_sche.new_password1)
    user_db = update_user_password(db=db, user=user_db, hashed_password=hashed_password)
    return user_db


@router.get("/get-menus", summary="获取当前用户菜单")
def get_current_user_menus(user_db: User = Depends(get_current_user)):
    """根据用户的角色获取相应的菜单"""

    menus = set()
    roles = user_db.roles
    for role in roles:
        for menu in role.menus:
            menus.add(menu)
    return list(menus)
