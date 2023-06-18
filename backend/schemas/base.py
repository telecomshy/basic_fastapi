from pydantic import BaseModel as PydanticBaseModel
from typing import Any


class BaseModel(PydanticBaseModel):
    """
    自定义BaseModel，方便全局修改模型配置
    """
    pass


class OutBaseModel(BaseModel):
    success = True
    message: str
    data: Any
