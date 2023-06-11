from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from backend.db.models.user import User, Permission


def create_user(sess: Session, username: str, password: str) -> User:
    """创建用户"""

    user = User(username=username, password=password)
    sess.add(user)
    sess.commit()
    return user


def get_user_by_id(sess: Session, user_id: int) -> User | None:
    """根据用户id获取用户"""

    return sess.get(User, user_id)


def get_user_by_username(sess: Session, username: str) -> User | None:
    """根据用户名获取用户"""

    stmt = select(User).filter_by(username=username)
    user = sess.execute(stmt).scalar()
    return user


def update_user_password(db: Session, user: User, hashed_password: str) -> User:
    """更新用户密码"""

    user.password = hashed_password
    db.commit()
    return user


def get_user_permissions(user: User) -> list[Permission]:
    """获取用户所有权限"""

    perms = set()
    for role in user.roles:
        for perm in role.perms:
            perms.add(perm)
    return list(perms)


def get_user_permission_scopes(user: User) -> list[str]:
    """获取用户权限域"""

    scopes = set()
    perms = get_user_permissions(user)

    for perm in perms:
        scope = perm.perm_rule.split("_")[1]
        scopes.add(scope)

    return list(scopes)


# TODO 缺少分页
def get_db_users(db: Session):
    """分页获取所有用户"""

    stmt = select(User).options(selectinload(User.roles))
    return db.scalars(stmt).all()
