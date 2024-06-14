import uuid
from sqlalchemy import Column, Integer, Text, DateTime, UUID, REAL

from .database import Base


class PageDiary(Base):
    __tablename__ = "pages_diary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    id_user = Column(UUID(as_uuid=True), nullable=False)
    pulse = Column(Integer, nullable=False)
    temperature = Column(REAL, nullable=False)
    upper_pressure = Column(Integer, nullable=False)
    lower_pressure = Column(Integer, nullable=False)
    oxygen_level = Column(Integer)
    sugar_level = Column(REAL)
    comment = Column(Text)
    create_date = Column(DateTime(timezone=True))
