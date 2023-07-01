from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.dependencies import session_db, authorization, current_user, RequiredPermissions
from backend.core.exceptions import ServiceException
from backend.core.utils import verify_password, get_password_hash
from backend.db.models.user import User
from backend.schemas.auth import UpdatePassIn, UpdatePassOut
from backend.schemas.user import QueryUsersOut, QueryRolesOut, UpdateUserIn, UpdateUserOut, QueryUserIn, DeleteUserIn, \
    DeleteUserOut
from backend.db.crud.user import query_users_db, query_roles_db, update_user_db, delete_user_db, update_user_db_password

router = APIRouter(dependencies=[Depends(authorization)])


@router.post("/users", response_model=QueryUsersOut, summary="获取用户列表")
def query_users(sess: Annotated[Session, Depends(session_db)], post_data: QueryUserIn):
    post_data = post_data.dict()
    post_data["page"] = post_data["page"] - 1  # 前端送过来的page从1开始，需要减1
    users_total, users_db = query_users_db(sess, **post_data)
    return {"message": "获取用户列表", "data": {"total": users_total, "users": users_db}}


@router.get("/roles", response_model=QueryRolesOut, summary="获取角色列表")
def query_roles(sess: Annotated[Session, Depends(session_db)]):
    roles_db = query_roles_db(sess)
    return {"message": "获取角色列表", "data": roles_db}


@router.post("/update-user", response_model=UpdateUserOut, summary="更新用户",
             dependencies=[Depends(RequiredPermissions('update_user'))])
def update_user(sess: Annotated[Session, Depends(session_db)], post_data: UpdateUserIn):
    print("in update user:", post_data)
    try:
        user_db = update_user_db(sess, post_data)
        return {"message": "更新用户", "data": user_db}
    except Exception:
        raise ServiceException(code="ERR_007", message="用户更新失败")


@router.post("/change-pass", summary="修改密码", response_model=UpdatePassOut)
def update_user_password(
        post_data: UpdatePassIn,
        sess: Annotated[Session, Depends(session_db)],
        user: Annotated[User, Depends(current_user)]
):
    """更新用户密码"""

    if not verify_password(post_data.old_password, user.password):
        raise ServiceException(code="ERR_004", message="原始密码不正确")

    hashed_password = get_password_hash(post_data.password1)
    try:
        user_db = update_user_db_password(sess=sess, user=user, hashed_password=hashed_password)
        return {"message": "修改密码", "data": user_db.id}
    except Exception:
        raise ServiceException(code="ERR_007", message="密码更新失败")


@router.post("/delete-user", summary="删除用户", response_model=DeleteUserOut,
             dependencies=[Depends(RequiredPermissions('delete_user'))])
def delete_users(sess: Annotated[Session, Depends(session_db)], post_data: DeleteUserIn):
    user_id = post_data.user_id

    if isinstance(user_id, int):
        user_id = [user_id]

    try:
        counts = delete_user_db(sess, user_id)
        return {"message": "删除用户", "data": counts}
    except Exception:
        raise ServiceException(code="ERR_007", message="用户删除失败")
