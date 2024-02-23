from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, relationship

from . import database


class Group(database.Base):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String)


class User(SQLAlchemyBaseUserTableUUID, database.Base):
    first_name = Column(String(length=128), nullable=False)
    surname = Column(String(length=128), nullable=False)
    last_name = Column(String(length=128))
    group_id = mapped_column(ForeignKey("group.id"), nullable=False)
    group = relationship("Group", uselist=False)
