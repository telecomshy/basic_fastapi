from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.dependencies import session_db, authorization
from backend.schemas.user import GetUsersOut, GetUserCountsOut, GetRolesOut, UpdateUserIn, UpdateUserOut, GetUserIn
from backend.db.crud.user import get_db_users, get_db_user_counts, get_db_roles, update_db_user

router = APIRouter(dependencies=[Depends(authorization)])


# @router.get("/users", response_model=GetUsersOut, summary="获取用户列表")
# def get_users(page: int, page_size: int, sess: Annotated[Session, Depends(session_db)]):
#     users_db = get_db_users(sess, page=page, page_size=page_size)
#     return {"message": "获取用户列表", "data": users_db}

@router.post("/users", response_model=GetUsersOut, summary="获取用户列表")
def get_users(sess: Annotated[Session, Depends(session_db)], post_data: GetUserIn):
    users_db = get_db_users(sess, **post_data.dict())
    return {"message": "获取用户列表", "data": users_db}


@router.get("/user-counts", response_model=GetUserCountsOut, summary="获取用户总数")
def get_user_counts(sess: Annotated[Session, Depends(session_db)]):
    user_counts = get_db_user_counts(sess)
    return {"message": "获取用户总数", "data": user_counts}


@router.get("/roles", response_model=GetRolesOut, summary="获取角色列表")
def get_roles(sess: Annotated[Session, Depends(session_db)]):
    roles_db = get_db_roles(sess)
    return {"message": "获取角色列表", "data": roles_db}


@router.post("/update-user", response_model=UpdateUserOut, summary="更新用户")
def update_user(sess: Annotated[Session, Depends(session_db)], updated_user: UpdateUserIn):
    user_db = update_db_user(sess, updated_user)
    return {"message": "更新用户", "data": user_db}
