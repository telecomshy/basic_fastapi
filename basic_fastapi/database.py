from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .config import settings


prod_engine = create_engine(settings.prod_database_url, connect_args={"check_same_thread": False})
ProdSession = sessionmaker(bind=prod_engine)

dev_engine = create_engine(settings.dev_database_url, connect_args={"check_same_thread": False})
DevSession = sessionmaker(bind=dev_engine)
