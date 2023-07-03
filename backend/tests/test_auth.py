from backend.db.crud.user import get_user_db_by_id, update_user_db_password
from backend.core.utils import verify_password, get_password_hash
from backend.core.config import settings
from backend.db.models.user import User


def test_register(client, session):
    """测试新增用户"""

    request_data = {
        "username": "test_user2",
        "password1": "Test_user2",
        "password2": "Test_user2"
    }

    result = client("/register", json=request_data)
    assert result["message"] == "用户ID"
    user_id = result["data"]
    user = session.get(User, user_id)
    assert user.username == "test_user2"
    assert verify_password("Test_user2", user.password)
    session.delete(user)
    session.commit()


def test_register_with_error_username(client):
    """测试新增用户时，添加数据库已有用户"""

    request_data = {
        "username": settings.test_username,
        "password1": settings.test_password,
        "password2": settings.test_password
    }
    result = client("/register", json=request_data)
    assert result["code"] == "ERR_002"
    assert result["message"] == "用户已存在"


def test_register_with_error_password(client):
    """测试新增用户时，输入不符合规范的密码"""

    request_data = {
        "username": "test_user3",
        "password1": "test123",
        "password2": "test123"
    }
    result = client("/register", json=request_data)
    assert result["code"] == "ERR_001"
    assert result["message"] == "数据验证错误"


def test_login(client, uuid_and_captcha):
    """测试用户成功登陆"""
    uuid, captcha = uuid_and_captcha

    request_data = {
        "username": settings.test_username,
        "password": settings.test_password,
        "uuid": uuid,
        "captcha": captcha
    }

    result = client("/login", json=request_data)
    assert result["message"] == "用户token"


def test_login_with_error_username(client, uuid_and_captcha):
    """测试用户登陆时，用户不存在"""
    uuid, captcha = uuid_and_captcha

    request_data = {
        "username": "test_err_user1",
        "password": "Test_user1",
        "uuid": uuid,
        "captcha": captcha
    }
    result = client("/login", json=request_data)
    assert result["code"] == "ERR_003"
    assert result["message"] == "用户名不存在"


def test_login_with_error_password(client, uuid_and_captcha):
    """测试用户登陆时，密码错误"""
    uuid, captcha = uuid_and_captcha

    request_data = {
        "username": settings.test_username,
        "password": "error_password",
        "uuid": uuid,
        "captcha": captcha
    }
    result = client("/login", json=request_data)
    assert result["code"] == "ERR_004"
    assert result["message"] == "密码不正确"


def test_login_with_error_captcha(client, uuid_and_captcha):
    """测试用户登陆验证码错误"""
    uuid, captcha = uuid_and_captcha
    captcha = "abc!"

    request_data = {
        "username": settings.test_username,
        "password": settings.test_password,
        "uuid": uuid,
        "captcha": captcha
    }
    result = client("/login", json=request_data)
    assert result["code"] == "ERR_005"
    assert result["message"] == "验证码错误"


def test_change_password(client, session):
    request_data = {
        "old_password": settings.test_password,
        "password1": "Test_user1_new",
        "password2": "Test_user1_new"
    }
    result = client("/change-pass", json=request_data)
    assert result["message"] == "已删除用户ID"
    user_id = result["data"]
    user = get_user_db_by_id(session, user_id)
    assert verify_password("Test_user1_new", user.password)
    hashed_password = get_password_hash(settings.test_password)
    update_user_db_password(session, user, hashed_password)


def test_change_password_with_error_password(client):
    request_data = {
        "old_password": "error_password",
        "password1": "Test_user1_new",
        "password2": "Test_user1_new"
    }
    result = client("/change-pass", json=request_data)
    assert result["code"] == "ERR_004"
    assert result["message"] == "原始密码不正确"
