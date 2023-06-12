from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.dependencies import session_db
from backend.schemas.userbase import GetUsersOut
from backend.db.crud.user import get_db_users

router = APIRouter()


@router.get("/users", response_model=GetUsersOut)
def get_users(page: int, page_size: int, sess: Session = Depends(session_db)):
    users = get_db_users(sess, page=page, page_size=page_size)
    return {"data": users}
