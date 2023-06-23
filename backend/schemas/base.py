from pydantic import BaseModel as PydanticBaseModel
from typing import Any
from backend.core.utils import to_camel


class BaseModel(PydanticBaseModel):
    """
    自定义BaseModel，方便全局修改模型配置
    """
    pass


class OutDataModel(BaseModel):
    success = True
    message: str
    data: Any


class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
