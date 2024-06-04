from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.ext.automap import automap_base
from .basemodel import Base
from .models import init_existing_models


class DatabaseInitializer:
    def __init__(self, base: DeclarativeBase) -> None:
        self.base: DeclarativeBase = base

    def init_database(self, postgres_dsn):
        engine = create_engine(postgres_dsn)
        session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.base.metadata.create_all(bind=engine)

        BaseMap = automap_base()
        BaseMap.prepare(engine, reflect=True)
        init_existing_models(BaseMap)

        return session_local


DB_INITIALIZER = DatabaseInitializer(Base())