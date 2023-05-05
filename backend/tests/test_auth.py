from backend.db.crud.users import get_user_by_username


def test_register(client, inited_db):
    """测试新增用户"""

    user = get_user_by_username(inited_db, "test_user2")
    if user:
        inited_db.delete(user)
        inited_db.commit()

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