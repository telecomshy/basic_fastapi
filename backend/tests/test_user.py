def test_get_users(client):
    users = client("/users")
    # print(users)
    assert users, "有效用户为空"
    users = client("/users?page_size=10&page=0")
    assert len(users) <= 10


def test_get_users_total(client):
    total = client("/users-total")
    print(total)
    assert total > 0
