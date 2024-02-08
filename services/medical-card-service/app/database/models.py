from sqlalchemy import Column, Integer, String, ForeignKey, UUID, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, relationship

from .database import Base


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSONB)
    id_template = Column(Integer)
    id_card = mapped_column(ForeignKey("cards.id"))
    create_date = Column(DateTime(timezone=True))
    card = relationship("Card", back_populates='pages')


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(UUID(as_uuid=True), nullable=False)
    user_name = Column(String)
    create_date = Column(DateTime(timezone=True))
    pages = relationship("Page", back_populates='card', cascade="all, delete-orphan")
