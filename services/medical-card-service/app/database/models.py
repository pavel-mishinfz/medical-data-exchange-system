from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, relationship

from .database import Base


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSONB)
    id_template = Column(Integer)
    id_card = mapped_column(ForeignKey("cards.id"))
    card = relationship("Card", back_populates='pages')


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer)
    user_name = Column(String)
    pages = relationship("Page", back_populates='card', cascade="all, delete-orphan")
