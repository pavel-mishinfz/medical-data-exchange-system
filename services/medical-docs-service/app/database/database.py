from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class DatabaseInitializer:
    def __init__(self, base) -> None:
        self.base = base

    def init_database(self, postgres_dsn):
        engine = create_engine(postgres_dsn)
        session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.base.metadata.create_all(bind=engine)
        return session_local


class Base(DeclarativeBase):
    pass


DB_INITIALIZER = DatabaseInitializer(Base())
