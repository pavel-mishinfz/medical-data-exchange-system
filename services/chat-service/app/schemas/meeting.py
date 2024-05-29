import uuid
from typing import Optional
from datetime import date
from pydantic import BaseModel, Field


class MeetingBase(BaseModel):
    """
    Базовая модель встречи
    """
    topic: Optional[str] = Field('Онлайн-консультация', title='Наименование встречи')

    class ConfiDict:
        from_attribute = True


class MeetingIn(MeetingBase):
    """
    Модель для добавления встречи в базу данных
    """
    record_id: uuid.UUID = Field(title='Идентификатор записи на прием')
    start_date: date = Field(title='Начало встречи (дата)')
    start_time: str = Field(title='Начало встречи (время)')


class MeetingDB(MeetingIn):
    """
    Модель для получения информации о встрече из базы данных
    """
    meeting_id: int


class Meeting(MeetingBase):
    """
    Модель для получения информации о встрече
    """
    start_url: str = Field(title='Ссылка для начала встречи')
    join_url: str = Field(title='Ссылка для присоединения к встречи')
    start_time: str = Field(title='Время встречи')

