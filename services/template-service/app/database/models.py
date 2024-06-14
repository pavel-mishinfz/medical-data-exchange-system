from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from .database import Base


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    structure = Column(ARRAY(JSONB), nullable=False)
    is_deleted = Column(Boolean, default=False)
