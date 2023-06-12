import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from sqlalchemy import select
from backend.db.models.user import User, Role
from backend.apis.v1.auth import get_password_hash, uuid_captcha_mapping
from backend.db.base import SessionDB
from ..main import app


@pytest.fixture(scope="session")
def fastapi_client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def inited_db():
    session = SessionDB()
    # 创建用户
    user = User(username="test_user1", password=get_password_hash("Test_user1"))
    # 创建角色
    for role_name in ["系统管理员", "普通用户"]:
        role = session.execute(select(Role).filter_by(role_name=role_name)).scalar()
        if role is None:
            role = Role(role_name=role_name)
        user.roles.append(role)
    # 关联用户和角色
    session.add(user)
    session.commit()
    yield session
    # 清理临时创建的用户
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
