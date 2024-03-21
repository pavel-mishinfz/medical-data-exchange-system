from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import mapped_column, relationship

from . import database


class Group(database.Base):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String)


class User(SQLAlchemyBaseUserTableUUID, database.Base):
    name = Column(String(length=128), nullable=False)
    surname = Column(String(length=128), nullable=False)
    patronymic = Column(String(length=128))
    birthday = Column(Date, nullable=False)
    specialization_id = mapped_column(ForeignKey("specialization.id"))
    img = Column(String)
    group_id = mapped_column(ForeignKey("group.id"), nullable=False)
    group = relationship("Group", uselist=False)


class Specialization(database.Base):
    __tablename__ = 'specialization'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False)
    doctors = relationship("User", backref="specialization")
