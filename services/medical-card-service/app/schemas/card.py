import uuid
import re

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from .address import AddressIn, AddressOptional
from .passport import PassportIn, PassportOptional
from .disability import DisabilityIn, DisabilityOptional
from .family_status import FamilyStatus
from .education import Education
from .busyness import Busyness


class CardBase(BaseModel):
    """
    Базовая модель медкарты
    """
    name: Optional[str] = None
    surname: Optional[str] = None
    patronymic: Optional[str] = Field(title='Отчество', default=None)
    is_man: Optional[bool] = None
    birthday: Optional[date] = None
    address: Optional[AddressOptional] = None
    phone: Optional[str] = None
    is_urban_area: Optional[bool] = None
    number_policy: Optional[str] = Field(title='Номер полиса', min_length=16, max_length=16, default=None)
    snils: Optional[str] = Field(title='СНИЛС', min_length=14, max_length=14, default=None)
    insurance_company: Optional[str] = None
    benefit_category_code: Optional[str] = Field(title='Код категории лояльности', default=None)
    passport: Optional[PassportOptional] = None
    disability: Optional[DisabilityIn] = Field(title='Инвалидность', default=None)
    workplace: Optional[str] = Field(title='Место работы', default=None)
    job: Optional[str] = Field(title='Должность', default=None)
    blood_type: Optional[str] = Field(title='Группа крови', max_length=30, default=None)
    rh_factor_is_pos: Optional[bool] = Field(title='Резус-фактор', default=None)
    allergy: Optional[str] = Field(title='Аллергические реакции', default=None)

    class ConfigDict:
        from_attribute = True


class CardIn(CardBase):
    """
    Модель для добавления медкарты
    """
    id_user: uuid.UUID
    name: str = Field(title='Имя')
    surname: str = Field(title='Фамилия')
    is_man: bool = Field(title='Пол')
    birthday: date = Field(title='Дата рождения')
    address: AddressIn = Field(title='Место регистрации')
    phone: str = Field(title='Номер телефона')
    is_urban_area: bool = Field(title='Сельская/городская местность')
    number_policy: str = Field(title='Номер полиса')
    snils: str = Field(title='СНИЛС')
    passport: PassportIn = Field(title='Паспорт')
    id_family_status: int = Field(title='Семейное положение')
    id_education: int = Field(title='Образование')
    id_busyness: int = Field(title='Занятость')

    @field_validator('name', 'surname', mode='before')
    @classmethod
    def validate_name(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        return v

    @field_validator('birthday', mode='before')
    @classmethod
    def validate_bday(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        try:
            parsed_date = datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError('Поле должно иметь формат даты')
        if parsed_date > date.today():
            raise ValueError('Дата не может быть больше текущей')
        return v

    @field_validator('phone', mode='before')
    @classmethod
    def validate_phone(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        if not re.match('^\+[0-9]{11}$', str(v)):
            raise ValueError('Значение должно быть в формате +7XXXXXXXXXX')
        return v

    @field_validator('number_policy', mode='before')
    @classmethod
    def validate_number_policy(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        if not re.match('^[0-9]{16}$', str(v)):
            raise ValueError('Значение должно быть длиной шестнадцать цифр')
        return v

    @field_validator('snils', mode='before')
    @classmethod
    def validate_snils(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        if not re.match('^[0-9]{3}-[0-9]{3}-[0-9]{3} [0-9]{2}$', str(v)):
            raise ValueError('Значение должно быть в формате XXX-XXX-XXX XX')
        return v


class Card(CardBase):
    """
    Модель используемая при запросе информации о медкарте
    """
    id: int = Field(title='Идентификатор медкарты')
    id_user: uuid.UUID
    family_status: FamilyStatus
    education: Education
    busyness: Busyness
    create_date: date = Field(title='Дата создания медкарты')


class CardOptional(CardBase):
    """
    Модель для обновления медкарты
    """
    id_family_status: Optional[int] = None
    id_education: Optional[int] = None
    id_busyness: Optional[int] = None
    disability: Optional[DisabilityOptional] = None

    @field_validator('name', 'surname', mode='before')
    @classmethod
    def validate_name(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        return v

    @field_validator('birthday', mode='before')
    @classmethod
    def validate_bday(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        try:
            parsed_date = datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError('Поле должно иметь формат даты')
        if parsed_date > date.today():
            raise ValueError('Дата не может быть больше текущей')
        return v

    @field_validator('phone', mode='before')
    @classmethod
    def validate_phone(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        if not re.match('^\+[0-9]{11}$', str(v)):
            raise ValueError('Значение должно быть в формате +7XXXXXXXXXX')
        return v

    @field_validator('number_policy', mode='before')
    @classmethod
    def validate_number_policy(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        if not re.match('^[0-9]{16}$', str(v)):
            raise ValueError('Значение должно быть длиной шестнадцать цифр')
        return v

    @field_validator('snils', mode='before')
    @classmethod
    def validate_snils(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        if not re.match('^[0-9]{3}-[0-9]{3}-[0-9]{3} [0-9]{2}$', str(v)):
            raise ValueError('Значение должно быть в формате XXX-XXX-XXX XX')
        return v


class CardIdsSelfAndPatient(BaseModel):
    """
    Модель для получения id медкарты и пациента
    """
    id: int
    id_user: uuid.UUID

    class ConfigDict:
        from_attribute = True