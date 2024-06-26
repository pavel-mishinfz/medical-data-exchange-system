from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime, Boolean
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
    specialization = relationship("Specialization", backref='users', uselist=False, lazy="selectin")
    desc = Column(String)
    date_employment = Column(Date)
    img = Column(String)
    group_id = mapped_column(ForeignKey("group.id"), nullable=False)
    group = relationship("Group", uselist=False)
    is_deleted = Column(Boolean, default=False)


class ConfirmCode(database.Base):
    __tablename__ = "confirm_code"

    user_id = mapped_column(ForeignKey("user.id"), primary_key=True, nullable=False, unique=True)
    code = Column(String(length=6), nullable=False)
    create_date = Column(DateTime(timezone=True), nullable=False)
    activation_time = Column(DateTime(timezone=True))


class Specialization(database.Base):
    __tablename__ = 'specialization'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False)
    img = Column(String, nullable=False)
