from pydantic import BaseModel as PydanticBaseModel
from typing import Any


class BaseModel(PydanticBaseModel):
    """
    自定义BaseModel，方便全局修改模型配置
    """
    pass


class ResponseBase(BaseModel):
    success: bool = True
    code: str = ""
    message: str = ""
    detail: str = ""
    data: Any

