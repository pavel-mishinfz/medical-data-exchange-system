import uuid
import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RecordBase(BaseModel):
    """
    Базовая модель записи на прием
    """
    date: Optional[datetime.date] = None
    time: Optional[str] = None
    is_online: bool = Field(False, title='Формат приема')

    class ConfigDict:
        from_attribute = True


class RecordIn(RecordBase):
    """
    Модель для добавления записи
    """
    id_user: uuid.UUID = Field(title='Идентификатор пациента')
    id_doctor: uuid.UUID = Field(title='Идентификатор врача')
    date: datetime.date = Field(title='Дата записи')
    time: str = Field(title='Время записи')


class Record(RecordBase):
    """
    Модель используемая при запросе информации о записи
    """
    id: uuid.UUID = Field(title='Идентификатор записи')
    id_user: uuid.UUID
    id_doctor: uuid.UUID


class RecordOptional(RecordBase):
    """
    Модель для обновления информации о записи
    """
    id_doctor: Optional[uuid.UUID] = None
