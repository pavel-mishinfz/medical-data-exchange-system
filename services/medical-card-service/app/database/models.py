import uuid

from sqlalchemy import Column, Integer, String, ForeignKey, UUID, Date, Boolean, DateTime, CHAR, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, relationship

from .database import Base


class Page(Base):
    __tablename__ = "pages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    data = Column(JSONB)
    id_template = Column(Integer, nullable=False)
    id_card = mapped_column(ForeignKey("cards.id"), nullable=False)
    id_doctor = Column(UUID(as_uuid=True), nullable=False)
    create_date = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, default=False)
    card = relationship("Card", back_populates='pages')
    documents = relationship("Document", backref='page', cascade='all, delete-orphan')


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(length=128), nullable=False)
    surname = Column(String(length=128), nullable=False)
    patronymic = Column(String(length=128))
    is_man = Column(Boolean, nullable=False)
    birthday = Column(Date, nullable=False)
    id_address = Column(Integer, ForeignKey('address.id'), nullable=False, unique=True)
    phone = Column(String(length=12), nullable=False, unique=True)
    is_urban_area = Column(Boolean, nullable=False)
    number_policy = Column(CHAR(length=16), nullable=False, unique=True)
    snils = Column(CHAR(length=14), nullable=False, unique=True)
    insurance_company = Column(String, nullable=False)
    benefit_category_code = Column(String)
    id_passport = Column(Integer, ForeignKey('passport.id'), nullable=False, unique=True)
    id_family_status = Column(Integer, ForeignKey('family_status.id'), nullable=False)
    id_education = Column(Integer, ForeignKey('education.id'), nullable=False)
    id_busyness = Column(Integer, ForeignKey('busyness.id'), nullable=False)
    id_disability = Column(Integer, ForeignKey('disability.id'))
    workplace = Column(String)
    job = Column(String)
    blood_type = Column(String(length=30))
    rh_factor_is_pos = Column(Boolean)
    allergy = Column(String)
    create_date = Column(Date, nullable=False)
    is_deleted = Column(Boolean, default=False)
    pages = relationship("Page", back_populates='card')
    address = relationship("Address", back_populates='card', uselist=False)
    passport = relationship("Passport", back_populates="card", uselist=False)
    family_status = relationship("FamilyStatus", backref="cards")
    education = relationship("Education", backref="cards")
    busyness = relationship("Busyness", backref="cards")
    disability = relationship("Disability", back_populates="card", uselist=False)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    id_page = mapped_column(ForeignKey('pages.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    path_to_file = Column(String, nullable=False)
    create_date = Column(Date, nullable=False)


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(length=128))
    district = Column(String(length=128))
    locality = Column(String(length=128), nullable=False)
    street = Column(String(length=128), nullable=False)
    house = Column(Integer, nullable=False)
    apartment = Column(Integer)
    card = relationship("Card", back_populates="address", uselist=False)


class Passport(Base):
    __tablename__ = 'passport'

    id = Column(Integer, primary_key=True, index=True)
    series = Column(CHAR(length=4), nullable=False)
    number = Column(CHAR(length=6), nullable=False)
    card = relationship("Card", back_populates="passport", uselist=False)


class FamilyStatus(Base):
    __tablename__ = 'family_status'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=50), nullable=False)


class Education(Base):
    __tablename__ = 'education'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=30), nullable=False)


class Busyness(Base):
    __tablename__ = 'busyness'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=128), nullable=False)


class Disability(Base):
    __tablename__ = 'disability'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    group = Column(Integer, nullable=False)
    create_date = Column(Date, nullable=False)
    card = relationship("Card", back_populates="disability", uselist=False)
