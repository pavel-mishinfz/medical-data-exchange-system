from sqlalchemy import Column, Integer, String, Text, DateTime

from .database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    id_page = Column(Integer)
    name = Column(String)
    description = Column(Text)
    id_template = Column(Integer)
    path_to_file = Column(String)
    create_date = Column(DateTime(timezone=True))
