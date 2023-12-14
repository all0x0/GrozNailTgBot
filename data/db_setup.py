from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={}, future=True, poolclass=NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def get_session():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
