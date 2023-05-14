from pydantic import Field, constr, EmailStr, validator
from backend.schemas.base import BaseModel

PASS_PAT = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?\d)(?=.*?[!@#$%^&*._-]).{8,}$"


class UserBaseSche(BaseModel):
    username: constr(min_length=6, max_length=20) = Field(..., title="用户名",
                                                          description="用户名不能少于6个字符，不能超过20个字符")


class UserRegisterSche(UserBaseSche):
    # 密码必须大于8个字符，包含大小写字母，数字以及特殊字符
    password1: constr(regex=PASS_PAT) = Field(..., title="密码",
                                              description="密码必须大于8个字符，且包含大小写字母、数字以及特殊字符")
    password2: str = Field(..., title="重复密码")
    email: EmailStr | None = Field(title="邮箱")
    phone_number: str | None = Field(title="手机号码")

    @validator("password2")
    def match_password(cls, v, values):
        # 检查密码是否匹配，如果password1验证失败，则不会在values中，所以需要先判断是否在values中
        if 'password1' in values and v != values['password1']:
            raise ValueError("两次输入的密码不一致")
        return v


class UserInfoSche(UserBaseSche):
    id: int = Field(title="用户ID")
    email: str | None = Field(title="邮箱")
    phone_number: str | None = Field(title="手机号码")

    class Config:
        orm_mode = True


class PassUpdateSche(BaseModel):
    old_password: str = Field(..., title="旧密码")
    new_password1: constr(regex=PASS_PAT) = Field(..., title="新密码",
                                                  description="密码必须大于8个字符，且包含大小写字母、数字以及特殊字符")
    new_password2: str = Field(..., title="重复新密码")

    @validator("new_password2")
    def match_password(cls, v, values):
        # 检查密码是否匹配，如果password1验证失败，则不会在values中，所以需要先判断是否在values中
        if 'new_password1' in values and v != values['new_password1']:
            raise ValueError("两次输入的新密码不一致")
        return v


class PermissionInfoSche(BaseModel):
    perm_name: str = Field(..., title="权限名称")
    perm_rule: str = Field(..., title="权限规则")

    class Config:
        orm_mode = True
