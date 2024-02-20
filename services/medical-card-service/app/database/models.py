from sqlalchemy import Column, Integer, String, ForeignKey, UUID, DateTime, Boolean, Date, CHAR
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, relationship

from .database import Base


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSONB)
    id_template = Column(Integer, nullable=False)
    id_card = mapped_column(ForeignKey("cards.id"), nullable=False)
    create_date = Column(DateTime(timezone=True), nullable=False)
    card = relationship("Card", back_populates='pages')


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(UUID(as_uuid=True), nullable=False)
    first_name = Column(String(length=128), nullable=False)
    surname = Column(String(length=128), nullable=False)
    last_name = Column(String(length=128))
    is_man = Column(Boolean, nullable=False)
    birthday_date = Column(Date, nullable=False)
    id_address = mapped_column(ForeignKey('address.id'), nullable=False)
    is_urban_area = Column(Boolean, nullable=False)
    number_policy = Column(CHAR(length=16), nullable=False, unique=True)
    snils = Column(CHAR(length=14), nullable=False, unique=True)
    insurance_company = Column(String, nullable=False)
    benefit_category_code = Column(String)
    id_passport = mapped_column(ForeignKey('passport.id'), nullable=False)
    id_family_status = mapped_column(ForeignKey('family_status.id'), nullable=False)
    id_education = mapped_column(ForeignKey('education.id'), nullable=False)
    id_busyness = mapped_column(ForeignKey('busyness.id'), nullable=False)
    id_disability = mapped_column(ForeignKey('disability.id'))
    workplace = Column(String)
    job = Column(String)
    blood_type = Column(CHAR(length=30))
    rh_factor_is_pos = Column(Boolean)
    allergy = Column(String)
    create_date = Column(DateTime(timezone=True), nullable=False)
    pages = relationship("Page", back_populates='card', cascade="all, delete-orphan")
    address = relationship("Address", uselist=False, cascade="all, delete")
    passport = relationship("Passport", uselist=False, cascade="all, delete")
    family_status = relationship("FamilyStatus", uselist=False)
    education = relationship("Education", uselist=False)
    busyness = relationship("Busyness", uselist=False)
    disability = relationship("Disability", uselist=False, cascade="all, delete")


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(length=128))
    district = Column(String(length=128))
    locality = Column(String(length=128), nullable=False)
    street = Column(String(length=128), nullable=False)
    house = Column(Integer, nullable=False)
    apartment = Column(Integer)
    phone = Column(String(length=12), nullable=False)


class Passport(Base):
    __tablename__ = 'passport'

    id = Column(Integer, primary_key=True, index=True)
    series = Column(CHAR(length=4), nullable=False)
    number = Column(CHAR(length=6), nullable=False)


class FamilyStatus(Base):
    __tablename__ = 'family_status'

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(length=50), nullable=False)


class Education(Base):
    __tablename__ = 'education'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(length=30), nullable=False)


class Busyness(Base):
    __tablename__ = 'busyness'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(length=128), nullable=False)


class Disability(Base):
    __tablename__ = 'disability'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    group = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
