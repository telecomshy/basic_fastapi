from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.db.models.users import User


def create_user(db: Session, username: str, password: str) -> User:
    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    return user


def get_user_by_username(db: Session, username) -> User:
    stmt = select(User).filter_by(username=username)
    user = db.scalar(stmt)
    return user
