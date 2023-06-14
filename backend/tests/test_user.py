def test_get_users(client, token):
    users = client("/users", headers={"Authorization": f"Bearer {token}"})
    assert "test_user1" in [user.username for user in users]


def test_get_users_total(client):
    total = client("/users-total")
    assert total > 0, total
