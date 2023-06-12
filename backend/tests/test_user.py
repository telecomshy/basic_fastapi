def test_get_users(client):
    users = client("/api/v1/users")
    assert users, "有效用户为空"
    users = client("/api/v1/users?page_size=10&page=0")
    assert len(users) <= 10
