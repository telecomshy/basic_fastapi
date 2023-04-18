from ..user.crud import get_user_by_username
from ..user.router import uuid_captcha_mapping
from uuid import uuid4


def test_register(client, inited_db):
    """测试新增用户"""

    user = get_user_by_username(inited_db, "test_user2")
    if user:
        inited_db.delete(user)
        inited_db.commit()

    request_data = {
        "username": "test_user2",
        "password": "Test_user2"
    }
    response = client.post("/register", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == "test_user2"
    assert data["phone_number"] is None


def test_register_with_error_username(client):
    """测试新增用户时，添加数据库已有用户"""

    request_data = {
        "username": "test_user1",
        "password": "Test_user1"
    }
    response = client.post("/register", json=request_data)
    assert response.status_code == 409


def test_register_with_error_password(client):
    """测试新增用户时，输入不符合规范的密码"""

    request_data = {
        "username": "test_user3",
        "password": "test123"
    }
    response = client.post("/register", json=request_data)
    assert response.status_code == 422


def test_login(client):
    """测试用户成功登陆"""

    uuid = str(uuid4())
    client.get(f"captcha?uuid={uuid}")
    captcha = uuid_captcha_mapping[uuid]

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


def test_login_with_error_username(client):
    """测试用户登陆，用户不存在"""

    request_data = {
        "username": "test_err_user1",
        "password": "Test_user1"
    }
    response = client.post("login", data=request_data)
    assert response.status_code == 401
    data = response.json()
    assert "Could not validate credentials" == data["detail"]


def test_login_with_error_password(client):
    """测试用户登陆，密码错误"""

    request_data = {
        "username": "test_user1",
        "password": "error_password"
    }
    response = client.post("login", data=request_data)
    assert response.status_code == 401
    data = response.json()
    assert "Could not validate credentials" == data["detail"]
