from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    id_card = Column(Integer)
    id_template = Column(Integer)
    data = Column(JSONB)


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer)
    user_name = Column(String)
