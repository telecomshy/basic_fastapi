from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.dependencies import session_db, authorization
from backend.schemas.user import UsersOut, UserCountsOut
from backend.db.crud.user import get_db_users, get_db_user_counts

router = APIRouter(dependencies=[Depends(authorization)])


@router.get("/users", response_model=UsersOut, summary="获取用户列表")
def get_users(page: int, page_size: int, sess: Annotated[Session, Depends(session_db)]):
    users = get_db_users(sess, page=page, page_size=page_size)
    return {"message": "获取用户列表", "data": users}


@router.get("/user-counts", response_model=UserCountsOut, summary="获取用户总数")
def get_user_counts(sess: Annotated[Session, Depends(session_db)]):
    user_counts = get_db_user_counts(sess)
    return {"message": "获取用户总数", "data": user_counts}

