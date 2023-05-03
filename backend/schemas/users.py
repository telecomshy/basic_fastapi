from pydantic import BaseModel, Field, constr, EmailStr, validator, SecretStr

PASS_PAT = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?\d)(?=.*?[!@#$%^&*._-]).{8,}$"


class UserBase(BaseModel):
    # username: str = Field(..., min_length=6, max_length=20, description="用户名不能少于6个字符，不能超过20个字符")
    username: constr(min_length=6, max_length=20)


class UserRegister(UserBase):
    # 密码必须大于8个字符，包含大小写字母，数字以及特殊字符
    password1: str = Field(..., regex=PASS_PAT, description="密码必须大于8个字符，且包含大小写字母、数字以及特殊字符")
    password2: str
    email: EmailStr | None
    phone_number: str | None

    @validator("password2")
    def match_password(cls, v, values):
        # 检查密码是否匹配，如果password1验证失败，则不会在values中，所以需要先判断是否在values中
        if 'password1' in values and v != values['password1']:
            raise ValueError("两次输入密码不一致")
        return v


class UserFull(UserBase):
    id: int
    email: str | None
    phone_number: str | None

    class Config:
        orm_mode = True
