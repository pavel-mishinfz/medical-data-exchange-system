from sqlalchemy import Column, Integer, String, UUID, Date, JSON, Boolean

from .database import Base


class Schedule(Base):
    __tablename__ = 'schedule'

    id = Column(Integer, primary_key=True, index=True)
    id_doctor = Column(UUID(as_uuid=True), nullable=False)
    schedule = Column(JSON, nullable=False)
    time_per_patient = Column(Integer, nullable=False)


class Record(Base):
    __tablename__ = "record"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(UUID(as_uuid=True), nullable=False)
    id_doctor = Column(UUID(as_uuid=True), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(String(length=30), nullable=False)
    is_online = Column(Boolean, nullable=False, default=False)

