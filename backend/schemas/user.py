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
    active: bool = Field(title="状态")
    email: str | None = Field(title="邮箱")
    phone_number: str | None = Field(title="手机号码")
    roles: list[Role]

    class Config:
        orm_mode = True


class QueryUserIn(BaseModel):
    page: int = Field(title="页码")
    page_size: int = Field(title="条目数", alias="pageSize")
    roles: list[int] | None = Field(title='角色ID列表')
    active: bool | None = Field(title="用户状态")
    others: str | None = Field(title="用户名、邮箱或手机号码")


class QueryUsersOut(OutDataModel):
    """获取所有用户信息"""

    class GetUsersOutData(BaseModel):
        total: int = Field(title="用户总数")
        users: list[User] = Field(tital="用户列表")

    data: GetUsersOutData


class QueryRolesOut(OutDataModel):
    data: list[Role] = Field(title="角色列表")


class UpdateUserIn(BaseModel):
    id: int = Field(title="用户ID")
    active: bool = Field(title="用户状态")
    email: str | None = Field(title="邮箱")
    phone_number: str | None = Field(title="手机号码", alias="phoneNumber")
    roles: list[int] = Field(title="角色ID列表")


class UpdateUserOut(OutDataModel):
    data: User


class DeleteUserIn(BaseModel):
    ids: int | list[int] = Field(title="用户ID或ID列表")