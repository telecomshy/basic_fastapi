from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    """
    自定义BaseModel，方便全局修改模型配置
    """
    pass
