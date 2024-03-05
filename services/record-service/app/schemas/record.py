import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RecordBase(BaseModel):
    """
    Базовая модель записи на прием
    """
    date: Optional[datetime] = None
    time: Optional[str] = None

    class ConfigDict:
        from_attribute = True


class RecordIn(RecordBase):
    """
    Модель для добавления записи
    """
    id_user: uuid.UUID = Field(title='Идентификатор пациента')
    id_doctor: uuid.UUID = Field(title='Идентификатор врача')
    date: datetime = Field(title='Дата записи')
    time: str = Field(title='Время записи')


class Record(RecordBase):
    """
    Модель используемая при запросе информации о записи
    """
    id: int = Field(title='Идентификатор записи')
    id_user: uuid.UUID
    id_doctor: uuid.UUID


class RecordOptional(RecordBase):
    """
    Модель для обновления информации о записи
    """
    id_doctor: Optional[uuid.UUID] = None


class RecordForPatient(RecordBase):
    """
    Модель используемая при запросе информации о всех записях для пациента
    """
    id_doctor: uuid.UUID


class RecordForDoctor(RecordBase):
    """
    Модель используемая при запросе информации о всех записях для врача
    """
    id_user: uuid.UUID
