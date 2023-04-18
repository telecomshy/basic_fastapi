from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine
from .config import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionDB = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
