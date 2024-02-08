from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import mapped_column, relationship

from .database import Base


class Diary(Base):
    __tablename__ = "diary"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer)
    pages = relationship('PageDiary', back_populates='diary', cascade="all, delete-orphan")


class PageDiary(Base):
    __tablename__ = 'page_diary'

    id = Column(Integer, primary_key=True, index=True)
    pulse = Column(Integer)
    comment = Column(Text)
    id_diary = mapped_column(ForeignKey('diary.id'))
    diary = relationship('Diary', back_populates='pages')
