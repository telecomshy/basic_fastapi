from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.dependencies import session_db, authorization
from backend.schemas.user import QueryUsersOut, QueryRolesOut, UpdateUserIn, UpdateUserOut, QueryUserIn
from backend.db.crud.user import get_db_users, get_db_roles, update_db_user

router = APIRouter(dependencies=[Depends(authorization)])


@router.post("/users", response_model=QueryUsersOut, summary="获取用户列表")
def get_users(sess: Annotated[Session, Depends(session_db)], post_data: QueryUserIn):
    post_data = post_data.dict()
    post_data["page"] = post_data["page"] - 1  # 前端送过来的page从1开始，需要减1
    users_total, users_db = get_db_users(sess, **post_data)
    return {"message": "获取用户列表", "data": {"total": users_total, "users": users_db}}


@router.get("/roles", response_model=QueryRolesOut, summary="获取角色列表")
def get_roles(sess: Annotated[Session, Depends(session_db)]):
    roles_db = get_db_roles(sess)
    return {"message": "获取角色列表", "data": roles_db}


@router.post("/update-user", response_model=UpdateUserOut, summary="更新用户")
def update_user(sess: Annotated[Session, Depends(session_db)], updated_user: UpdateUserIn):
    user_db = update_db_user(sess, updated_user)
    return {"message": "更新用户", "data": user_db}
