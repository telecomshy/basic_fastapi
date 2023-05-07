from sqlalchemy.orm import Session
from sqlalchemy import select, update
from backend.db.models.users import User


def create_user(db: Session, username: str, password: str) -> User:
    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    return user


def get_user_by_username(db: Session, username: str) -> User:
    stmt = select(User).filter_by(username=username)
    user = db.scalar(stmt)
    return user


def update_user_password(db: Session, user: User, hashed_password: str) -> User:
    user.password = hashed_password
    db.commit()
    return user
