from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    class Config:
        error_msg_templates = {
            "value_error.missing": "字段不能为空",
            "value_error.any_str.min_length": "长度不对"
        }


