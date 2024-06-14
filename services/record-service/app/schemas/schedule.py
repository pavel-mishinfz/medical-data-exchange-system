import uuid
import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator


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

    @field_validator('schedule', mode='before')
    @classmethod
    def validate_schedule(cls, value):
        if not isinstance(value, dict):
            raise ValueError('Поле schedule должно быть словарем')
        for k, v in value.items():
            if k not in map(str, range(7)):
                raise ValueError('Ключами schedule должны быть целые числа от 0 до 6')
            if not isinstance(v, str) or not re.match('^\d{2}:\d{2}-\d{2}:\d{2}$', v):
                raise ValueError('Значения времени должны быть в формате 00:00-00:00')
        return value
    
    @field_validator('time_per_patient', mode='before')
    @classmethod
    def validate_time_per_patient(cls, v):
        if v is None:
            raise ValueError('Поле <Время приема> не должно быть пустым')
        if not isinstance(v, int):
            try:
                int(v)
            except ValueError:
                raise ValueError('Поле <Время приема> должно иметь целочисленный тип')
        if int(v) <= 0:
            raise ValueError('Поле <Время приема> должно содержать положительное число')
        return int(v)


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
    @field_validator('schedule', mode='before')
    @classmethod
    def validate_schedule(cls, value):
        if not isinstance(value, dict):
            raise ValueError('Поле schedule должно быть словарем')
        for k, v in value.items():
            if k not in map(str, range(7)):
                raise ValueError('Ключами schedule должны быть целые числа от 0 до 6')
            if not isinstance(v, str) or not re.match('^\d{2}:\d{2}-\d{2}:\d{2}$', v):
                raise ValueError('Значения времени должны быть в формате 00:00-00:00')
        return value
    
    @field_validator('time_per_patient', mode='before')
    @classmethod
    def validate_time_per_patient(cls, v):
        if v is None:
            raise ValueError('Поле <Время приема> не должно быть пустым')
        if not isinstance(v, int):
            try:
                int(v)
            except ValueError:
                raise ValueError('Поле <Время приема> должно иметь целочисленный тип')
        if int(v) <= 0:
            raise ValueError('Поле <Время приема> должно содержать положительное число')
        return int(v)
