from sqlalchemy import Column, Integer, CHAR, UUID, ForeignKey, Date
from sqlalchemy.orm import mapped_column, relationship

from .database import Base


class TimeRecord(Base):
    __tablename__ = "time_record"

    id = Column(Integer, primary_key=True, index=True)
    time = Column(CHAR(length=10), nullable=False)


class Record(Base):
    __tablename__ = "record"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(UUID(as_uuid=True), nullable=False)
    id_doctor = Column(UUID(as_uuid=True), nullable=False)
    date = Column(Date, nullable=False)
    id_time = mapped_column(ForeignKey('time.id'), nullable=False)
    time = relationship(TimeRecord, uselist=False)

