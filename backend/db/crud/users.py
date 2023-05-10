from sqlalchemy.orm import Session
from sqlalchemy import select, update
from backend.db.models.users import User, Role, Permission


def create_user(db: Session, username: str, password: str) -> User:
    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    return user


def get_user_by_username(db: Session, username: str) -> User:
    """根据用户名获取用户"""

    stmt = select(User).filter_by(username=username)
    user = db.scalar(stmt)
    return user


def update_user_password(db: Session, user: User, hashed_password: str) -> User:
    """更新用户密码"""

    user.password = hashed_password
    db.commit()
    return user


def get_user_permissions(user: User) -> set[Permission]:
    """获取用户所有权限"""

    perms = set()
    for role in user.roles:
        for perm in role.perms:
            perms.add(perm)
    return perms
