from pydantic import Field
from backend.schemas.base import BaseModel, OutDataModel, CamelModel


class Role(CamelModel):
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

    class Config:
        orm_mode = True


class GetUsersOut(OutDataModel):
    """获取所有用户信息"""

    data: list[User] = Field(title="用户列表")


class GetUserIn(BaseModel):
    page: int = Field(title="页码")
    page_size: int = Field(title="条目数", alias="pageSize")
    username: str | None = Field(title="用户名")
    roles: list[int] | None = Field(title='角色ID列表')


class GetUserCountsOut(OutDataModel):
    """获取所有用户数量"""

    data: int = Field(title="用户总数")


class GetRolesOut(OutDataModel):
    data: list[Role] = Field(title="角色列表")


class UpdateUserIn(BaseModel):
    id: int = Field(title="用户ID")
    email: str | None = Field(title="邮箱")
    phone_number: str | None = Field(title="手机号码", alias="phoneNumber")
    roles: list[int] = Field(title="角色ID列表")


class UpdateUserOut(OutDataModel):
    data: User
