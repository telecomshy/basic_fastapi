from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    class Config:
        error_msg_templates = {
            "value_error.missing": "不能为空",
            "value_error.any_str.min_length": "最少需要{limit_value}个字符"
        }
