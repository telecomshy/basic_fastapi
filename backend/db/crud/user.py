from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func
from backend.db.models.user import User, Permission, Role


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


def change_user_password(sess: Session, user: User, hashed_password: str) -> User:
    """更新用户密码"""

    user.password = hashed_password
    sess.commit()
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


def get_db_users(db: Session, page: int = None, page_size: int = None) -> list[User]:
    """分页获取所有用户"""

    # 使用selectinload策略，避免懒加载，一次性读取和user相关的role信息
    stmt = select(User).options(selectinload(User.roles))
    if page_size is not None:
        stmt = stmt.limit(page_size)
    if page is not None:
        stmt = stmt.offset(page * page_size)
    return list(db.scalars(stmt))


def get_db_user_counts(db: Session) -> int:
    stmt = select(func.count()).select_from(User)
    return db.execute(stmt).scalar()


def get_db_roles(db: Session) -> list[Role]:
    return list(db.scalars(select(Role)))
