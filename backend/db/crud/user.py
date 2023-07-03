from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func, delete
from backend.db.models.user import User, Permission, Role
from backend.schemas.user import UpdateUserIn
from backend.core.utils import get_password_hash


def register_user_db(sess: Session, username: str, password: str) -> User:
    """创建用户"""

    user = User(username=username, password=password, active=True)
    # 新注册的用户用户都是普通用户
    role = sess.scalar(select(Role).filter_by(role_name="普通用户"))
    user.roles.append(role)
    sess.add(user)
    sess.commit()
    return user


def get_user_db_by_id(sess: Session, user_id: int) -> User | None:
    """根据用户id获取用户"""

    return sess.get(User, user_id)


def get_user_db_by_username(sess: Session, username: str) -> User | None:
    """根据用户名获取用户"""

    stmt = select(User).filter_by(username=username)
    user = sess.execute(stmt).scalar()
    return user


def update_user_db_password(sess: Session, user: User, hashed_password: str) -> User:
    """更新用户密码"""

    user.password = hashed_password
    sess.commit()
    return user


def get_user_db_permissions(user: User) -> list[Permission]:
    """获取用户所有权限"""

    perms = set()
    for role in user.roles:
        for perm in role.perms:
            perms.add(perm)
    return list(perms)


def get_user_db_permission_scopes(user: User) -> list[str]:
    """获取用户权限域"""

    scopes = set()
    perms = get_user_db_permissions(user)

    for perm in perms:
        scope = perm.perm_rule.split("_")[1]
        scopes.add(scope)

    return list(scopes)


def query_users_db(
        db: Session,
        page: int = None,
        page_size: int = None,
        roles: list[int] = None,
        active: bool = None,
        others: str = None,
) -> tuple[int, list[User]]:
    """分页获取所有用户"""

    stmt = select(User)
    count_stmt = select(func.count()).select_from(User)

    # 根据用户名，邮箱，电话等模糊查询
    if others is not None:
        others_condition = User.username.like(f"%{others}%") | User.email.like(f"%{others}%") | User.phone_number.like(
            f"%{others}%")
        stmt = stmt.filter(others_condition)
        count_stmt = count_stmt.filter(others_condition)

    # 根据角色查询
    if roles:  # roles可能为空列表，此时也意味着返回所有角色
        roles_condition = Role.id.in_(roles)
        stmt = stmt.join(User.roles).filter(roles_condition)
        count_stmt = count_stmt.join(User.roles).filter(roles_condition)

    if active is not None:
        active_condition = User.active.is_(active)
        stmt = stmt.filter(active_condition)
        count_stmt = count_stmt.filter(active_condition)

    users_total = db.scalar(count_stmt)

    if page_size is not None:
        stmt = stmt.limit(page_size)
    if page is not None:
        stmt = stmt.offset(page * page_size)

    users = list(db.scalars(stmt))

    return users_total, users


def get_roles_db(sess: Session) -> list[Role]:
    return list(sess.scalars(select(Role)))


def update_user_db(sess: Session, update_user: UpdateUserIn):
    user = sess.get(User, update_user.id)
    user.email, user.phone_number, user.active = update_user.email, update_user.phone_number, update_user.active
    user.roles = [sess.get(Role, id_) for id_ in update_user.roles]
    sess.add(user)
    sess.commit()
    return user


def delete_user_db(sess: Session, users_id: list[int]):
    # 注意，如果使用sess.execute(delete(User).where(User.id.in_(user_ids)))这样的语句，不会删除关联对象
    for user_id in users_id:
        user = sess.get(User, user_id)
        sess.delete(user)
    sess.commit()
    return len(users_id)
