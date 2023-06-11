from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.dependencies import session_db
from backend.schemas.user import GetUsersOut, User
from backend.db.crud.user import get_db_users
from backend.core.utils import NormalizedResponseRoute

router = APIRouter()


@router.get("/users", response_model=GetUsersOut)
def get_users(sess: Session = Depends(session_db)):
    users = get_db_users(sess)
    return {"data": users}
