from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine
from backend.core.config import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False}, echo=True)
SessionDB = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
