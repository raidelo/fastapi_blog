from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DB_URL = "sqlite:///./blog.db"

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
