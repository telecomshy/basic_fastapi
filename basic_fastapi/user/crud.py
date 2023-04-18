from sqlalchemy.orm import Session
from sqlalchemy import select
from . import models


def create_user(db: Session, username: str, password: str) -> models.User:
    user = models.User(username=username, password=password)
    db.add(user)
    db.commit()
    return user


def get_user_by_username(db: Session, username) -> models.User:
    stmt = select(models.User).filter_by(username=username)
    user = db.scalar(stmt)
    return user
