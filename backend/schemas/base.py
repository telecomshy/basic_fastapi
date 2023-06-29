from pydantic import BaseModel as PydanticBaseModel, validator
from typing import Any
from backend.core.utils import to_camel


class BaseModel(PydanticBaseModel):
    """
    自定义BaseModel，方便全局修改模型配置
    """

    # 前端如果为空时，默认为传入空字符串，因此需要把所有空字符串转换为None
    @validator('*', pre=True)
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v


class OutDataModel(BaseModel):
    success = True
    message: str
    data: Any


class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
