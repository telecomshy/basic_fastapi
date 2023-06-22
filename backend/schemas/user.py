from pydantic import Field, validator
from backend.schemas.base import BaseModel, OutDataModel, CamelModel


class Role(BaseModel):
    id: int = Field("角色ID")
    role_name: str = Field("角色名称")

    class Config:
        orm_mode = True


class User(CamelModel):
    id: int = Field(title="用户ID")
    username: str = Field(title="用户名")
    email: str | None = Field(title="邮箱")
    phone_number: str | None = Field(title="手机号码")
    roles: list[Role]

    @validator("roles")
    def process_roles(cls, v, values):
        return ','.join(role.role_name for role in v)

    class Config:
        orm_mode = True


class UsersOut(OutDataModel):
    """获取所有用户信息"""

    data: list[User]


class UserCountsOut(OutDataModel):
    """获取所有用户数量"""

    data: int
