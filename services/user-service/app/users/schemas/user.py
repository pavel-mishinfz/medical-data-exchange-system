import datetime
import uuid
from typing import Optional

from fastapi_users import schemas
from pydantic import Field, BaseModel


class UserRead(schemas.BaseUser[uuid.UUID]):
    name: str = Field(title='Имя пользователя')
    surname: str = Field(title='Фамилия пользователя')
    patronymic: str = Field(title='Отчество пользователя')
    group_id: int = Field(title='Индентификатор группы')
    birthday: datetime.date = Field(title='Возраст')
    specialization_id: Optional[int] = Field(None, title='Специализация врача')
    img: Optional[str] = Field(None, title='Фотография пользователя')
    date_employment: Optional[datetime.date] = None
    desc: Optional[str] = None


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


class UserReadSummary(BaseModel):
    id: uuid.UUID
    name: str
    surname: str
    patronymic: str
    birthday: datetime.date

    class ConfigDict:
        from_attribute = True


class DoctorRead(BaseModel):

    id: uuid.UUID
    name: str
    surname: str
    patronymic: str
    specialization_id: int
    img: str
    date_employment: datetime.date
    desc: str

    class ConfigDict:
        from_attribute = True