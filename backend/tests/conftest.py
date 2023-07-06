import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from sqlalchemy import select
from backend.db.models.model_user import User, Role
from backend.apis.v1.auth import uuid_captcha_mapping
from backend.db.crud.crud_user import get_user_by_username
from backend.db.base import SessionDB
from backend.main import app
from backend.core.config import settings
from backend.core.dependencies import current_user, session_db, authorization
from backend.core.utils import get_password_hash
from fastapi import Depends
from sqlalchemy.orm import Session


def override_current_user(db: Session = Depends(session_db)) -> User:
    user = get_user_by_username(db, settings.test_username)
    return user


# 注意，depends参数不能随意设置，任何参数都会从路径函数的传参中去查找
def override_authorization():
    return True


app.dependency_overrides[current_user] = override_current_user
app.dependency_overrides[authorization] = override_authorization


@pytest.fixture(scope="session")
def fastapi_client() -> TestClient:
    return TestClient(app)


# session应该是函数级别的scope，这样一个请求一个session
@pytest.fixture
def session():
    sess = SessionDB()
    try:
        yield sess
    finally:
        sess.close()


def create_test_user():
    with SessionDB() as sess, sess.begin():
        user = User(username=settings.test_username, password=get_password_hash(settings.test_password), active=True)
        # 创建角色
        for role_name in ["系统管理员", "普通用户"]:
            role = sess.execute(select(Role).filter_by(role_name=role_name)).scalar()
            if role is None:
                role = Role(role_name=role_name)
            user.roles.append(role)
        # 关联用户和角色
        sess.add(user)


def delete_test_user():
    with SessionDB() as sess, sess.begin():
        user = get_user_by_username(sess, settings.test_username)
        sess.delete(user)


@pytest.fixture(scope="session", autouse=True)
def mock_data():
    create_test_user()
    yield
    delete_test_user()


@pytest.fixture(scope="session")
def client(fastapi_client):
    def _request(url, *args, **kwargs):
        method = getattr(fastapi_client, 'post') if kwargs.get("json") else getattr(fastapi_client, 'get')
        return method(f"{settings.base_url}{url}", *args, **kwargs).json()

    return _request


@pytest.fixture(scope="session")
def uuid_and_captcha(fastapi_client):
    """
    创建登陆时需要的uuid和captcha
    """
    uuid = str(uuid4())
    fastapi_client.get(f"{settings.base_url}/captcha?uuid={uuid}")
    captcha = uuid_captcha_mapping[uuid]
    return uuid, captcha
