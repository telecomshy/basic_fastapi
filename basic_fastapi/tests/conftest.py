import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from ..main import app
from ..database import DevSession
from ..user.models import User
from ..user.router import get_password_hash
from ..dependencies import get_db
from ..user.router import uuid_captcha_mapping


def override_get_db():
    session = DevSession()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def inited_db():
    session = DevSession()
    password = get_password_hash("Test_user1")
    user = User(username="test_user1", password=password)
    session.add(user)
    session.commit()
    yield session
    session.delete(user)
    session.commit()
    session.close()


@pytest.fixture()
def uuid_and_captcha(client):
    """
    创建登陆时需要的uuid和captcha
    """
    uuid = str(uuid4())
    client.get(f"captcha?uuid={uuid}")
    captcha = uuid_captcha_mapping[uuid]
    return uuid, captcha
