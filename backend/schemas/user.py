from pydantic import Field, constr, EmailStr, validator
from backend.schemas.base import BaseModel


class UserCommon(BaseModel):
    id: int = Field(title="用户ID")
    username: str = Field(title="用户名")
    email: str | None = Field(title="邮箱")
    phone_number: str | None = Field(title="手机号码")

    class Config:
        orm_mode = True
