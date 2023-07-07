from typing import Annotated
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse, Response, FileResponse
from sqlalchemy.orm import Session
from backend.core.dependencies import session_db, authorization, current_user, RequiredPermissions
from backend.core.exceptions import ServiceException
from backend.core.utils.helpers import verify_password, get_password_hash, query_result_to_csv, query_result_to_file
from backend.core.config import settings
from backend.db.models import model_user
from backend.schemas import schema_user, schema_auth
from backend.db.crud import crud_user

router = APIRouter()


@router.post(
    "/users",
    response_model=schema_user.QueryUsersOut,
    summary="获取用户列表"
)
def query_users(
        sess: Annotated[Session, Depends(session_db)],
        post_data: schema_user.QueryUserIn
):
    post_data = post_data.dict()
    post_data["page"] = post_data["page"] - 1  # 前端送过来的page从1开始，需要减1
    users_total, users_db = crud_user.query_users(sess, **post_data)
    return {"message": "用户总数及用户列表", "data": {"total": users_total, "users": users_db}}


@router.get(
    "/roles",
    response_model=schema_user.QueryRolesOut,
    summary="获取角色列表"
)
def query_roles(sess: Annotated[Session, Depends(session_db)]):
    roles_db = crud_user.get_roles(sess)
    return {"message": "角色列表", "data": roles_db}


@router.post(
    "/update-user",
    response_model=schema_user.UpdateUserOut,
    summary="更新用户",
    dependencies=[Depends(RequiredPermissions('update_user'))]
)
def update_user(
        sess: Annotated[Session, Depends(session_db)],
        post_data: schema_user.UpdateUserIn
):
    try:
        user_db = crud_user.update_user(
            sess,
            user_id=post_data.id,
            phone_number=post_data.phone_number,
            email=post_data.email,
            roles_id=post_data.roles_id,
            active=post_data.active
        )
        return {"message": "已更新用户信息", "data": user_db}
    except Exception:
        raise ServiceException(code="ERR_007", message="用户更新失败")


@router.post("/change-pass", summary="修改密码", response_model=schema_auth.UpdatePassOut)
def change_user_password(
        post_data: schema_auth.UpdatePassIn,
        sess: Annotated[Session, Depends(session_db)],
        user_db: Annotated[model_user.User, Depends(current_user)]
):
    """更新用户密码"""
    if not verify_password(post_data.old_password, user_db.password):
        raise ServiceException(code="ERR_004", message="原始密码不正确")

    hashed_password = get_password_hash(post_data.password1)
    try:
        user_db = crud_user.update_user_password(sess=sess, user=user_db, hashed_password=hashed_password)
        return {"message": "已删除用户ID", "data": user_db.id}
    except Exception:
        raise ServiceException(code="ERR_007", message="密码更新失败")


@router.post(
    "/delete-user",
    summary="删除用户",
    response_model=schema_user.DeleteUserOut,
    dependencies=[Depends(RequiredPermissions('delete_user'))]
)
def delete_users(
        sess: Annotated[Session, Depends(session_db)],
        post_data: schema_user.DeleteUserIn
):
    user_id = post_data.user_id
    users_id = [user_id] if isinstance(user_id, int) else user_id

    try:
        counts = crud_user.delete_user(sess, users_id)
        return {"message": "删除用户数", "data": counts}
    except Exception:
        raise ServiceException(code="ERR_007", message="删除用户失败")


@router.get(
    "/current-user",
    summary="获取当前用户名",
    response_model=schema_user.CurrentUserNameOut
)
def get_current_user(user_db: Annotated[model_user.User, Depends(current_user)]):
    try:
        return {"message": "当前用户名", "data": user_db.username}
    except Exception:
        raise ServiceException(code="ERR_007", message="获取当前用户名失败")


@router.get(
    "/current-user-scope",
    summary="获取当前用户所有域",
    response_model=schema_user.CurrentUserScopeOut
)
def get_current_user_scopes(user_db: Annotated[model_user.User, Depends(current_user)]):
    try:
        return {"message": "当前用户所有域", "data": crud_user.get_user_permission_scopes(user_db)}
    except Exception:
        raise ServiceException(code="ERR_007", message="获取当前用户所有域失败")


@router.get(
    "/reset-pass",
    summary="重置用户密码",
    response_model=schema_user.ResetUserPasswordOut
)
def reset_user_password(
        sess: Annotated[Session, Depends(session_db)],
        user_id: Annotated[int, Query(alias="userId")],
):
    try:
        user_db = crud_user.get_user_by_id(sess, user_id)
        init_pass = settings.init_password
        hashed_init_pass = get_password_hash(settings.init_password)
        crud_user.update_user_password(sess, user_db, hashed_init_pass)
        return {"message": "初始密码", "data": init_pass}
    except Exception:
        raise ServiceException(code="ERR_007", message="重置密码失败")


@router.post(
    "/create-user",
    summary="创建用户",
    response_model=schema_user.CreateUserOut
)
def create_user(
        sess: Annotated[Session, Depends(session_db)],
        post_data: schema_user.CreateUserIn
):
    if crud_user.get_user_by_username(sess, post_data.username):
        raise ServiceException(code="ERR_002", message="用户已存在")

    hashed_password = get_password_hash(settings.init_password)
    try:
        user_id = crud_user.create_user(
            sess,
            username=post_data.username,
            password=hashed_password,
            roles_id=post_data.roles_id
        )
        return {"message": "新建用户ID", "data": user_id}
    except Exception:
        raise ServiceException(code="ERR_007", message="创建用户失败")


@router.get("/export-csv", response_class=StreamingResponse)
def export_users(sess: Annotated[Session, Depends(session_db)]):
    # users = crud_user.query_users(sess)[1]
    # header = ["username", "email", "phone_number"]
    # file = query_result_to_csv(header, users)
    def iter_file():
        with open('backend/temp_file.csv', 'rb') as f:
            yield from f

    return StreamingResponse(iter_file(), media_type="text/csv")


@router.get("/export-file", response_class=FileResponse)
def export_users(sess: Annotated[Session, Depends(session_db)]):
    users = crud_user.query_users(sess)[1]
    header = ["username", "email", "phone_number"]
    query_result_to_file(header, users)
    return FileResponse("backend/temp_file.csv")
