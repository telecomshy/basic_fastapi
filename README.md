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

## 2. 开发规范

- schema模型字段注释统一使用`Constrained Types`进行约束，右侧使用`Field`定制openAPI文档。
- 内部抛出的异常统一使用自定义的`HTTPException`，并传入`reason`关键字参数，表明错误原因，方便前端统一处理。
- 为了区分pydantic模型和sqlalchemy模型，pydantic模型类统一使用`[名词][用途动词][Sche后缀]`为类名，如`UserRegisterSche`
  ，小写加下划线为变量名，如`user_register_sche`，sqlalchemy仅使用名词为类名，而在路径函数中，变量名统一加`_db`后缀。
- 原则上数据库的`crud`操作不对返回对象为空进行判断，判断统一在路径函数中进行判断处理。