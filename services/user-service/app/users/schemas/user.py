import datetime
import uuid
import re
from typing import Optional

from fastapi_users import schemas
from pydantic import Field, BaseModel, field_validator

from .specialization import Specialization


class UserRead(schemas.BaseUser[uuid.UUID]):
    name: str = Field(title='Имя пользователя')
    surname: str = Field(title='Фамилия пользователя')
    patronymic: Optional[str] = Field(None, title='Отчество пользователя')
    group_id: int = Field(title='Индентификатор группы')
    birthday: datetime.date = Field(title='Возраст')
    specialization_id: Optional[int] = Field(None, title='Специализация врача')
    img: Optional[str] = Field(None, title='Фотография пользователя')
    date_employment: Optional[datetime.date] = None
    desc: Optional[str] = None
    is_deleted: bool


class UserCreate(schemas.BaseUserCreate):
    name: str
    surname: str
    patronymic: Optional[str] = None
    group_id: int
    birthday: datetime.date
    specialization_id: Optional[int] = None
    img: Optional[str] = None
    date_employment: Optional[datetime.date] = None
    desc: Optional[str] = None
    is_deleted: Optional[bool] = False

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        if not re.fullmatch('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', v):
            raise ValueError('Email некорректной формы')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        return v

    @field_validator('name', 'surname')
    @classmethod
    def validate_name_and_surname(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        return v
    
    @field_validator('birthday', mode='before')
    @classmethod
    def validate_bday(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        try:
            parsed_date = datetime.datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError('Поле должно иметь формат даты')
        if parsed_date > datetime.date.today():
            raise ValueError('Дата не может быть больше текущей')
        return v
    
    @field_validator('specialization_id', mode='before')
    @classmethod
    def validate_spec(cls, v, values):
        group_id = values.data.get('group_id')
        if group_id == 2:
            if v is None:
                raise ValueError('Поле не должно быть пустым')
            if not isinstance(v, int):
                raise ValueError('Поле должно иметь целочисленный тип')
            if v <= 0:
                raise ValueError('Поле должно иметь значение больше 0')
        return v
    
    @field_validator('date_employment', mode='before')
    @classmethod
    def validate_date_employment(cls, v, values):
        group_id = values.data.get('group_id')
        if group_id == 2:
            if v is None or not v.strip():
                raise ValueError('Поле не должно быть пустым')
            try:
                parsed_date = datetime.datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError('Поле должно иметь формат даты')
            if parsed_date > datetime.date.today():
                raise ValueError('Дата не может быть больше текущей')
        return v

    @field_validator('desc')
    @classmethod
    def validate_desc(cls, v, values):
        group_id = values.data.get('group_id')
        if group_id == 2:
            if v is None or not v.strip():
                raise ValueError('Поле не должно быть пустым')
        return v


class UserUpdate(schemas.BaseUserUpdate):
    name: Optional[str] = None
    surname: Optional[str] = None
    patronymic: Optional[str] = None
    group_id: Optional[int] = None
    birthday: Optional[datetime.date] = None
    specialization_id: Optional[int] = None
    img: Optional[str] = None
    date_employment: Optional[datetime.date] = None
    desc: Optional[str] = None
    is_deleted: Optional[bool] = False

    @field_validator('name', 'surname')
    @classmethod
    def validate_name_and_surname(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        return v
    
    @field_validator('birthday', mode='before')
    @classmethod
    def validate_bday(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        try:
            parsed_date = datetime.datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError('Поле должно иметь формат даты')
        if parsed_date > datetime.date.today():
            raise ValueError('Дата не может быть больше текущей')
        return v
    
    @field_validator('specialization_id', mode='before')
    @classmethod
    def validate_spec(cls, v, values):
        group_id = values.data.get('group_id')
        if group_id == 2:
            if v is None:
                raise ValueError('Поле не должно быть пустым')
            if not isinstance(v, int):
                raise ValueError('Поле должно иметь целочисленный тип')
            if v <= 0:
                raise ValueError('Поле должно иметь значение больше 0')
        return v
    
    @field_validator('date_employment', mode='before')
    @classmethod
    def validate_date_employment(cls, v, values):
        group_id = values.data.get('group_id')
        if group_id == 2:
            if v is None or not v.strip():
                raise ValueError('Поле не должно быть пустым')
            try:
                parsed_date = datetime.datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError('Поле должно иметь формат даты')
            if parsed_date > datetime.date.today():
                raise ValueError('Дата не может быть больше текущей')
        return v

    @field_validator('desc')
    @classmethod
    def validate_desc(cls, v, values):
        group_id = values.data.get('group_id')
        if group_id == 2:
            if v is None or not v.strip():
                raise ValueError('Поле не должно быть пустым')
        return v


class UserReadSummary(BaseModel):
    id: uuid.UUID
    name: str
    surname: str
    patronymic: Optional[str] = None
    birthday: datetime.date
    specialization: Optional[Specialization] = None
    img: Optional[str] = None
    date_employment: Optional[datetime.date] = None
    desc: Optional[str] = None
    is_superuser: bool

    class ConfigDict:
        from_attribute = True
