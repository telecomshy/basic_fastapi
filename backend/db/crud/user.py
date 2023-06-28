from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func
from backend.db.models.user import User, Permission, Role
from backend.schemas.user import UpdateUserIn


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


def get_db_users(
        db: Session,
        page: int = None,
        page_size: int = None,
        roles: list[int] = None,
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

    users_total = db.scalar(count_stmt)

    if page_size is not None:
        stmt = stmt.limit(page_size)
    if page is not None:
        stmt = stmt.offset(page * page_size)

    users = list(db.scalars(stmt))

    return users_total, users


def get_db_roles(db: Session) -> list[Role]:
    return list(db.scalars(select(Role)))


def update_db_user(db: Session, updated_user: UpdateUserIn):
    user = db.get(User, updated_user.id)
    user.email, user.phone_number = updated_user.email, updated_user.phone_number
    user.roles = [db.get(Role, id_) for id_ in updated_user.roles]
    db.add(user)
    db.commit()
    return user
