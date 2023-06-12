from backend.db.crud.user import get_user_by_username
from backend.main import app
from backend.core.dependencies import current_user, session_db
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.db.models.user import User


def override_get_current_user(db: Session = Depends(session_db)) -> User:
    user = get_user_by_username(db, 'test_user1')
    return user


app.dependency_overrides[current_user] = override_get_current_user


def test_register(client, inited_db):
    """测试新增用户"""

    request_data = {
        "username": "test_user2",
        "password1": "Test_user2",
        "password2": "Test_user2"
    }

    try:
        data = client("/api/v1/register", json=request_data)
        assert "id" in data
        assert data["username"] == "test_user2"
    finally:
        # 删除创建的用户
        test_user2 = get_user_by_username(inited_db, "test_user2")
        if test_user2:
            inited_db.delete(test_user2)
            inited_db.commit()


def test_register_with_error_username(client):
    """测试新增用户时，添加数据库已有用户"""

    request_data = {
        "username": "test_user1",
        "password1": "Test_user1",
        "password2": "Test_user1"
    }
    err_code, message = client("/api/v1/register", json=request_data)
    assert err_code == "ERR_002"
    assert message == "用户已存在"


def test_register_with_error_password(client):
    """测试新增用户时，输入不符合规范的密码"""

    request_data = {
        "username": "test_user3",
        "password1": "test123",
        "password2": "test123"
    }
    err_code, message = client("/api/v1/register", json=request_data)
    assert err_code == "ERR_001"
    assert message == "数据验证错误"


def test_login(client, uuid_and_captcha):
    """测试用户成功登陆"""
    uuid, captcha = uuid_and_captcha

    request_data = {
        "username": "test_user1",
        "password": "Test_user1",
        "uuid": uuid,
        "captcha": captcha
    }

    data = client("/api/v1/login", json=request_data)
    assert "token" in data
    assert data["username"] == "test_user1"


def test_login_with_error_username(client, uuid_and_captcha):
    """测试用户登陆时，用户不存在"""
    uuid, captcha = uuid_and_captcha

    request_data = {
        "username": "test_err_user1",
        "password": "Test_user1",
        "uuid": uuid,
        "captcha": captcha
    }
    code, message = client("/api/v1/login", json=request_data)
    assert code == "ERR_003"
    assert message == "用户名不存在"


def test_login_with_error_password(client, uuid_and_captcha):
    """测试用户登陆时，密码错误"""
    uuid, captcha = uuid_and_captcha

    request_data = {
        "username": "test_user1",
        "password": "error_password",
        "uuid": uuid,
        "captcha": captcha
    }
    code, message = client("/api/v1/login", json=request_data)
    assert code == "ERR_004"
    assert message == "密码不正确"


def test_login_with_error_captcha(client, uuid_and_captcha):
    """测试用户登陆验证码错误"""
    uuid, captcha = uuid_and_captcha
    captcha = "abc!"

    request_data = {
        "username": "test_user1",
        "password": "Test_user1",
        "uuid": uuid,
        "captcha": captcha
    }
    code, message = client("/api/v1/login", json=request_data)
    assert code == "ERR_005"
    assert message == "验证码错误"

