from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field


class BaseModel(PydanticBaseModel):
    """
    自定义BaseModel，方便全局修改模型配置
    """
    pass


class ResponseBaseModel(PydanticBaseModel):
    success: bool = Field(default=True, title="成功标识")
