def test_get_users(client, session):
    result = client("/users", json={"page": 0, "pageSize": 10})
    users = result["data"]["users"]
    total = result["data"]["total"]
    assert total > 0
    assert result["message"] == "用户总数及用户列表"
    assert "test_user1" in [user["username"] for user in users]
