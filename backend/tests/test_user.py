def test_get_users(client):
    result = client("/users?page=0&page_size=10")
    users = result["data"]
    assert "test_user1" in [user["username"] for user in users]


def test_get_users_total(client, token):
    result = client("/users-total", headers={"Authorization": f"Bearer {token}"})
    total_user = result["data"]
    assert total_user > 0
