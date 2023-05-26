from pydantic import BaseModel
from pydantic import Field


class RequestBaseModel(BaseModel):
    """
    自定义BaseModel，方便全局修改模型配置
    """
    pass


class ResponseBaseModel(BaseModel):
    success: bool = Field(default=True, title="成功标识")
