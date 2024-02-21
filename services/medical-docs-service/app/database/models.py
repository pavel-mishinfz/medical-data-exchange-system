from sqlalchemy import Column, Integer, String, Text, DateTime

from .database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    id_page = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    path_to_file = Column(String, nullable=False)
    create_date = Column(DateTime(timezone=True), nullable=False)
