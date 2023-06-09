import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from ..main import app
from backend.db.models.user import User
from backend.apis.v1.auth import get_password_hash, uuid_captcha_mapping
from backend.db.base import SessionDB


@pytest.fixture(scope="session")
def fastapi_client() -> TestClient:
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
def uuid_and_captcha(fastapi_client):
    """
    创建登陆时需要的uuid和captcha
    """
    uuid = str(uuid4())
    fastapi_client.get(f"/api/v1/captcha?uuid={uuid}")
    captcha = uuid_captcha_mapping[uuid]
    return uuid, captcha


@pytest.fixture()
def client(fastapi_client):
    def _request(url, **kwargs):
        if kwargs.get("json"):
            method = getattr(fastapi_client, 'post')
        else:
            method = getattr(fastapi_client, 'get')

        result = method(url, **kwargs).json()
        if result["success"]:
            return result["data"]
        return result["code"], result["message"]

    return _request
