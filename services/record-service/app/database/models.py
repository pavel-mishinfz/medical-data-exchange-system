from sqlalchemy import Column, Integer, String, UUID, Date

from .database import Base


class Record(Base):
    __tablename__ = "record"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(UUID(as_uuid=True), nullable=False)
    id_doctor = Column(UUID(as_uuid=True), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(String(length=10), nullable=False)

