from backend.db.crud.users import get_user_by_username
from backend.main import app
from backend.core.dependencies import get_current_user, get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.db.models.users import User


def override_get_current_user(db: Session = Depends(get_db)) -> User:
    user = get_user_by_username(db, 'test_user1')
    return user


app.dependency_overrides[get_current_user] = override_get_current_user


def test_register(client, inited_db):
    """测试新增用户"""

    request_data = {
        "username": "test_user2",
        "password1": "Test_user2",
        "password2": "Test_user2"
    }
    response = client.post("/register", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == "test_user2"
    assert data["phone_number"] is None
    # 删除创建的用户
    test_user2 = get_user_by_username(inited_db, "test_user2")
    inited_db.delete(test_user2)
    inited_db.commit()


def test_register_with_error_username(client):
    """测试新增用户时，添加数据库已有用户"""

    request_data = {
        "username": "test_user1",
        "password1": "Test_user1",
        "password2": "Test_user1"
    }
    response = client.post("/register", json=request_data)
    assert response.status_code == 409


def test_register_with_error_password(client):
    """测试新增用户时，输入不符合规范的密码"""

    request_data = {
        "username": "test_user3",
        "password1": "test123",
        "password2": "test123"
    }
    response = client.post("/register", json=request_data)
    assert response.status_code == 422
    error_type = response.json()['detail'][0]['type']
    assert error_type == 'value_error.str.regex'


def test_login(client, uuid_and_captcha):
    """测试用户成功登陆"""
    uuid, captcha = uuid_and_captcha

    request_data = {
        "username": "test_user1",
        "password": "Test_user1",
        "uuid": uuid,
        "captcha": captcha
    }
    response = client.post("login", data=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
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
    response = client.post("login", data=request_data)
    assert response.status_code == 401
    data = response.json()
    assert "用户名或密码错误" == data["reason"]


def test_login_with_error_password(client, uuid_and_captcha):
    """测试用户登陆时，密码错误"""
    uuid, captcha = uuid_and_captcha

    request_data = {
        "username": "test_user1",
        "password": "error_password",
        "uuid": uuid,
        "captcha": captcha
    }
    response = client.post("login", data=request_data)
    assert response.status_code == 401
    data = response.json()
    assert "用户名或密码错误" == data["reason"]


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
    response = client.post("login", data=request_data)
    assert response.status_code == 401
    data = response.json()
    assert "验证码错误" == data["reason"]


def test_update_user_password(client):
    request_data = {
        "old_password": "Test_user1",
        "new_password1": "Test_user1_temp",
        "new_password2": "Test_user1_temp"
    }

    response = client.post("update-pass", json=request_data)
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == "test_user1"


def test_update_user_password_with_error_old_password(client):
    request_data = {
        "old_password": "Test_user1_wrong_password",
        "new_password1": "Test_user1_temp",
        "new_password2": "Test_user1_temp"
    }

    response = client.post("update-pass", json=request_data)
    assert response.status_code == 401
    data = response.json()
    assert data["reason"] == "原始密码错误"


def test_update_user_password_with_dismatch_new_password(client):
    request_data = {
        "old_password": "Test_user1",
        "new_password1": "Test_user1_temp1",
        "new_password2": "Test_user1_temp2"
    }

    response = client.post("update-pass", json=request_data)
    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["msg"] == "两次输入的新密码不一致"
