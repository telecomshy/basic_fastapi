import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from ..main import app
from backend.db.models.users import User
from backend.apis.router_auth import get_password_hash, uuid_captcha_mapping
from backend.db.base import SessionDB


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def inited_db():
    session = SessionDB()
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
