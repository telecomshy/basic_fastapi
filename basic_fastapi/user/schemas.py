from pydantic import BaseModel, Field, constr


class UserBase(BaseModel):
    username: str = Field(..., min_length=6, max_length=20, description="用户名不能少于6个字符，不能超过20个字符")


class UserRegister(UserBase):
    password: constr(regex=r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?\d)(?=.*?[!@#$%^&*._-]).{8,}$") = \
        Field(..., description="密码必须大于8个字符，且包含大小写字母、数字以及特殊字符")


class UserFull(UserBase):
    id: int
    phone_number: str | None

    class Config:
        orm_mode = True
