from sqlalchemy import Column, Integer, Text, DateTime, UUID

from .database import Base


class PageDiary(Base):
    __tablename__ = "pages_diary"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(UUID(as_uuid=True), nullable=False)
    pulse = Column(Integer)
    comment = Column(Text)
    create_date = Column(DateTime(timezone=True))
