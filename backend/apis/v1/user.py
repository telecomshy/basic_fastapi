from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.core.dependencies import session_db, authorization
from backend.schemas.user import GetUsersOut, GetUsersTotalOut
from backend.db.crud.user import get_db_users, get_db_users_total

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/openapi-login")
# 添加oauth2_scheme是为了openapi能够获得授权，生产环境可以删除
router = APIRouter(dependencies=[Depends(authorization), Depends(oauth2_scheme)])


@router.get("/users", response_model=GetUsersOut)
def get_users(page: int, page_size: int, sess: Session = Depends(session_db)):
    users = get_db_users(sess, page=page, page_size=page_size)
    return {"data": users}


@router.get("/users-total", response_model=GetUsersTotalOut)
def get_users_total(sess: Session = Depends(session_db)):
    return {"data": get_db_users_total(sess)}
