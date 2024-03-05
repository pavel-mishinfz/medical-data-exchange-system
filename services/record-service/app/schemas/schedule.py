import uuid
from typing import Optional

from pydantic import BaseModel, Field


class ScheduleBase(BaseModel):
    """
    Базовая модель графика работы
    """
    schedule: Optional[dict] = None
    time_per_patient: Optional[int] = None

    class ConfigDict:
        from_attribute = True


class ScheduleIn(ScheduleBase):
    """
    Модель для добавления графика работы
    """
    id_doctor: uuid.UUID = Field(title='Идентификатор врача')
    schedule: dict = Field(title='Дни и время работы')
    time_per_patient: int = Field(title='Время приема одного пациента')


class Schedule(ScheduleBase):
    """
    Модель используемая при запросе информации о графике работы
    """
    id: int = Field(title='Идентификатор графика работы')
    id_doctor: uuid.UUID


class ScheduleOptional(ScheduleBase):
    """
    Модель для обновления информации о графике работы
    """
    pass
