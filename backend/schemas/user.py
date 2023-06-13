from pydantic import Field
from backend.schemas.base import BaseModel


class RoleBase(BaseModel):
    role_name: str = Field("角色名称")

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    id: int = Field(title="用户ID")
    username: str = Field(title="用户名")
    email: str | None = Field(title="邮箱")
    phone_number: str | None = Field(title="手机号码")
    roles: list[RoleBase]

    class Config:
        orm_mode = True


class GetUsersOut(BaseModel):
    """获取所有用户信息"""

    success: bool = True
    data: list[UserBase] = []


class GetUsersTotalOut(BaseModel):
    """获取所有用户数量"""

    success: bool = True
    data: int
