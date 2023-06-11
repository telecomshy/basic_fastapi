from pydantic import Field
from backend.schemas.base import BaseModel


class Role(BaseModel):
    role_name: str = Field("角色名称")

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int = Field(title="用户ID")
    username: str = Field(title="用户名")
    email: str | None = Field(title="邮箱")
    phone_number: str | None = Field(title="手机号码")
    roles: list[Role]

    class Config:
        orm_mode = True


class GetUsersOut(BaseModel):
    success: bool = True
    data: list[User] = []
