from backend.core.config import settings
from backend.db.crud import crud_user
from backend.core.utils.helpers import verify_password, get_password_hash


def test_get_users(client, session):
    result = client("/users", json={"page": 0, "pageSize": 10})
    users = result["data"]["users"]
    total = result["data"]["total"]
    assert total > 0
    assert result["message"] == "用户总数及用户列表"
    assert "test_user1" in [user["username"] for user in users]


def test_change_password(client, session):
    request_data = {
        "old_password": settings.test_password,
        "password1": "Test_user1_new",
        "password2": "Test_user1_new"
    }
    result = client("/change-pass", json=request_data)
    assert result["message"] == "已删除用户ID"
    user_id = result["data"]
    user = crud_user.get_user_by_id(session, user_id)
    assert verify_password("Test_user1_new", user.password)
    hashed_password = get_password_hash(settings.test_password)
    crud_user.update_user_password(session, user, hashed_password)


def test_change_password_with_error_password(client):
    request_data = {
        "old_password": "error_password",
        "password1": "Test_user1_new",
        "password2": "Test_user1_new"
    }
    result = client("/change-pass", json=request_data)
    assert result["code"] == "ERR_004"
    assert result["message"] == "原始密码不正确"
