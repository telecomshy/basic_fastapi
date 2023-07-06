from sqlalchemy.orm import Session
from sqlalchemy import select, func
from backend.db.models.model_user import User, Permission, Role


def register_user(sess: Session, username: str, password: str) -> int:
    """创建用户"""

    user = User(username=username, password=password, active=True)
    # 新注册的用户用户都是普通用户
    role = sess.scalar(select(Role).filter_by(role_name="普通用户"))
    user.roles.append(role)
    sess.add(user)
    sess.commit()
    return user.id


def create_user(sess: Session, *, username: str, password: str, roles_id: list[int]) -> User:
    user = User(username=username, password=password)
    user.roles.extend([sess.get(Role, role_id) for role_id in roles_id])
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


def update_user_password(sess: Session, user: User, hashed_password: str) -> User:
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


def query_users(
        db: Session,
        *,
        page: int,
        page_size: int,
        roles: list[int] | None = None,
        active: bool | None = None,
        others: str | None = None,
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


def get_roles(sess: Session) -> list[Role]:
    return list(sess.scalars(select(Role)))


def update_user(
        sess: Session,
        *,
        user_id: int | None,
        email: str | None,
        phone_number: str | None,
        active: bool,
        roles_id: list[int]
) -> User:
    user = sess.execute(select(User).filter_by(id=user_id)).scalar_one()  # 若不存在则抛出错误
    user.email, user.phone_number, user.active = email, phone_number, active
    user.roles_id = [sess.get(Role, id_) for id_ in roles_id]
    sess.add(user)
    sess.commit()
    return user


def delete_user(sess: Session, users_id: list[int]):
    # 注意，如果使用sess.execute(delete(User).where(User.id.in_(user_ids)))这样的语句，不会删除关联对象
    for user_id in users_id:
        user = sess.get(User, user_id)
        sess.delete(user)
    sess.commit()
    return len(users_id)
