from pydantic import Field, constr, validator
from uuid import UUID
from backend.schemas.base import BaseModel, OutDataModel

PASS_PAT = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?\d)(?=.*?[!@#$%^&*._-]).{8,}$"


class Password(BaseModel):
    # 密码必须大于8个字符，包含大小写字母，数字以及特殊字符
    password1: constr(regex=PASS_PAT) = Field(title="密码",
                                              description="密码必须大于8个字符，且包含大小写字母、数字以及特殊字符")
    password2: str = Field(title="重复密码")

    @validator("password2")
    def match_password(cls, v, values):
        # 检查密码是否匹配，如果password1验证失败，则不会在values中，所以需要先判断是否在values中
        if 'password1' in values and v != values['password1']:
            raise ValueError("两次输入的密码不一致")
        return v


class RegisterIn(Password):
    username: constr(min_length=6, max_length=20) = Field(title="用户名",
                                                          description="用户名不能少于6个字符，不能超过20个字符")


class RegisterOut(OutDataModel):
    data: int = Field(title="注册用户ID")


class LoginIn(BaseModel):
    uuid: UUID = Field(title="UUID")
    captcha: str = Field(title="验证码")
    username: str = Field(title="用户名")
    password: str = Field(title="密码")


class LoginOut(OutDataModel):
    class Data(BaseModel):
        token: str = Field(title="TOKEN")

    data: Data


class UpdatePassIn(Password):
    old_password: str = Field(title="旧密码")


class UpdatePassOut(OutDataModel):
    data: int = Field(title="用户ID")