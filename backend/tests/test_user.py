def test_get_users(client):
    result = client("/users?page=0&page_size=10")
    users = result["data"]
    assert result["message"] == "获取用户列表"
    assert "test_user1" in [user["username"] for user in users]


def test_get_users_total(client):
    result = client("/user-counts")
    total_user = result["data"]
    assert result["message"] == "获取用户总数"
    assert total_user > 0
