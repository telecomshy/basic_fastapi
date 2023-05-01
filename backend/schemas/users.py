from pydantic import BaseModel, Field, constr, EmailStr, validator

PASS_PAT = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?\d)(?=.*?[!@#$%^&*._-]).{8,}$"


class UserBase(BaseModel):
    username: str = Field(..., min_length=6, max_length=20, description="用户名不能少于6个字符，不能超过20个字符")


class UserRegister(UserBase):
    # 密码必须大于8个字符，包含大小写字母，数字以及特殊字符
    password1: constr(regex=PASS_PAT) = Field(..., description="密码必须大于8个字符，且包含大小写字母、数字以及特殊字符")
    password2: str
    email: EmailStr | None
    phone_number: str | None

    @validator("password2")
    def match_password(cls, v, values):
        # 检查密码是否匹配
        if 'password1' in values and v != values['password1']:
            raise ValueError("密码不匹配")
        return v


class UserFull(UserBase):
    id: int
    email: str | None
    phone_number: str | None

    class Config:
        orm_mode = True
