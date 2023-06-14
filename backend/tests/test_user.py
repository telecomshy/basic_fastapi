def test_get_users(client, token):
    users = client("/users?page=0&page_size=10", headers={"Authorization": f"Bearer {token}"})
    assert "test_user1" in [user["username"] for user in users]


def test_get_users_total(client, token):
    total = client("/users-total", headers={"Authorization": f"Bearer {token}"})
    assert total > 0, total
