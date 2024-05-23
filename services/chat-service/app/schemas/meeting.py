from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class MettingBase(BaseModel):
    """
    Базовая модель встречи
    """
    topic: str = Field(title='Наименование встречи')
    duration: int = Field(title='Продолжительность встречи')

    class ConfiDict:
        from_attribute = True


class MettingIn(MettingBase):
    """
    Модель для добавления встречи в базу данных
    """
    start_date: date = Field(title='Начало встречи (дата)')
    start_time: str = Field(title='Начало встречи (время)')


class Metting(MettingBase):
    """
    Модель для получения информации о встрече
    """
    id: int = Field(title='Идентификатор встречи')
    start_url: str = Field(title='Ссылка для начала встречи')
    join_url: str = Field(title='Ссылка для присоединения к встречи')
    password: str = Field(title='Пароль')
    start_time: str = Field(title='Время встречи')
    status: str = Field(title='Статус')

