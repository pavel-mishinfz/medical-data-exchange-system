import datetime
import uuid
from typing import Optional

from fastapi_users import schemas
from pydantic import Field


class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name: str = Field(title='Имя пользователя')
    surname: str = Field(title='Фамилия пользователя')
    last_name: str = Field(title='Отчество пользователя')
    group_id: int = Field(title='Индентификатор группы')
    birthday_date: datetime.date = Field(title='Дата рождения')
    specialization_id: Optional[int] = Field(None, title='Специализация врача')
    img: Optional[str] = Field(None, title='Фотография пользователя')


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    surname: str
    last_name: Optional[str] = None
    group_id: int
    birthday_date: datetime.date
    specialization_id: Optional[int] = None
    img: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    first_name: Optional[str] = None
    surname: Optional[str] = None
    last_name: Optional[str] = None
    group_id: Optional[int] = None
    birthday_date: Optional[datetime.date] = None
    specialization_id: Optional[int] = None
    img: Optional[str] = None
