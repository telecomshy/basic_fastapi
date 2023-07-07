from pydantic import BaseModel as PydanticBaseModel, validator, Field
from typing import Any
from backend.core.utils.helpers import to_camel


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

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class OutDataModel(BaseModel):
    success: bool = Field(True, title="成功标志")
    message: str = Field(title="接口说明")
    data: Any = Field(title="响应数据")
