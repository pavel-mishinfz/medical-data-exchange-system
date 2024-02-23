import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RecordBase(BaseModel):
    """
    Базовая модель записи на прием
    """
    id_user: Optional[uuid.UUID] = None
    id_doctor: Optional[uuid.UUID] = None
    date: Optional[datetime] = None
    id_time: Optional[int] = None

    class ConfigDict:
        from_attribute = True


class RecordIn(RecordBase):
    """
    Модель для добавления записи
    """
    id_user: Optional[uuid.UUID] = Field(title='Идентификатор пациента')
    id_doctor: Optional[uuid.UUID] = Field(title='Идентификатор врача')
    date: Optional[datetime] = Field(title='Дата записи')
    id_time: Optional[int] = Field(title='Время записи')


class Record(RecordBase):
    """
    Модель используемая при запросе информации о записи
    """
    pass


class RecordOptional(RecordBase):
    """
    Модель для обновления информации о записи
    """
    pass
