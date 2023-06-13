from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.dependencies import session_db, current_user
from backend.schemas.user import GetUsersOut, GetUsersTotalOut
from backend.db.crud.user import get_db_users, get_db_users_total

router = APIRouter(dependencies=[Depends(current_user)])


@router.get("/users", response_model=GetUsersOut)
def get_users(page: int, page_size: int, sess: Session = Depends(session_db)):
    users = get_db_users(sess, page=page, page_size=page_size)
    return {"data": users}


@router.get("/users-total", response_model=GetUsersTotalOut)
def get_users_total(sess: Session = Depends(session_db)):
    return {"data": get_db_users_total(sess)}
