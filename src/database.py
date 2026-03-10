from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = Path(__file__).parent.parent
DB_NAME = "blog.db"

SQLALCHEMY_DB_URL = f"sqlite:///{BASE_DIR / DB_NAME}"

engine = create_engine(SQLALCHEMY_DB_URL)

SessionMaker = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_db():
    with SessionMaker() as session:
        yield session


class Base(DeclarativeBase):
    pass
