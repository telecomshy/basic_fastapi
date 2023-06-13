# basic_fastapi

## 1. 项目结构

- `main.py`，项目入口
- `tests`，保存所有测试用例，和api模块对应
- `schemas`，保存所有`pydantic`模型
    - `base.py`，自定义的`BaseModel`，方便全局进行模型定制
    - 其它schema文件，和api模块对应
- `db`，数据库相关
    - `base.py`，数据`engine`和`Base`模型类
    - `models`，保存所有模型类
    - `crud`，数据库增删改查操作
- `core`，核心文件
    - `config.py`，项目配置
    - `dependencies.py`，fastapi全局依赖
    - `exceptions.py`，自定义异常
    - `utils.py`，工具函数
- `apis`，所有接口
    - `v1`，每个版本一个文件夹，保存所有api模块
    - `base.py`，路由注册

## 2. 规范和注意事项

- schema模型字段注释统一使用`Constrained Types`进行约束，右侧使用`Field`定制openAPI文档。
  覆盖默认异常处理器，统一返回200响应。
  - 正常返回：
    ```
    {"success": True, "data": data}
    ```
    对于正常返回，所有路径函数都提供了`response_model`，在schema模型中设置了`success`默认为True，
    因此在路径函数中，统一返回`{"data": data}`即可。  
  - 异常返回：
    ```
    {"success": False, "code": code, "message": message, "detail": detail}
    ```
    对于业务异常，直接抛出自定义的`ServiceException`即可，虽然是抛出一个异常，但实际上返回的是200的
    的相应。
- 数据库`crud`操作不对返回对象为空进行判断，统一在依赖或路径函数中进行判断处理。


## 3. 错误代码
应与前端保持一致：
- ERR_001: 数据验证错误
- ERR_002: 用户已经存在
- ERR_003: 用户名不存在
- ERR_004: 密码不正确
- ERR_005: 验证码错误
- ERR_006: token过期或解析失败