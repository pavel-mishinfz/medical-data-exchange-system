from sqlalchemy import Column, Integer, String, Boolean

from .database import Base


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    path_to_file = Column(String, nullable=False)
