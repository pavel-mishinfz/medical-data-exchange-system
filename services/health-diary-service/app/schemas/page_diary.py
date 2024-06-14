from datetime import datetime
from typing import Optional
import uuid
import re

from pydantic import BaseModel, Field, field_validator


class PageDiaryBase(BaseModel):
    """
    Базовая модель страницы дневника здоровья
    """
    pulse: Optional[int] = None
    temperature: Optional[float] = None
    upper_pressure: Optional[int] = None
    lower_pressure: Optional[int] = None
    oxygen_level: Optional[int] = Field(None, title='Показатель кислорода в крови')
    sugar_level: Optional[float] = Field(None, title='Показатель сахара в крови')
    comment: Optional[str] = Field(None, title='Комментарий о своем здоровье')

    class ConfigDict:
        from_attribute = True


class PageDiaryIn(PageDiaryBase):
    """
    Модель для добавления страницы дневника
    """
    pulse: int = Field(title='Показатель пульса')
    temperature: float = Field(title='Показатель температуры')
    upper_pressure: int = Field(title='Показатель верхнего артериального давления')
    lower_pressure: int = Field(title='Показатель нижнего артериального давления')

    @field_validator('pulse', 'upper_pressure', 'lower_pressure', mode='before')
    @classmethod
    def validate_required_integer_fields(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        if not isinstance(v, int):
            try:
                int(v)
            except ValueError:
                raise ValueError('Поле должно иметь целочисленный тип')
        return int(v)
    
    @field_validator('temperature', mode='before')
    @classmethod
    def validate_temperature(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        if not isinstance(v, float):
            try:
                float(v)
            except ValueError:
                raise ValueError('Поле должно иметь вещественный тип')
        if float(v) < 34.0 or float(v) > 43.0:
            raise ValueError('Некорректное значение')
        return float(v)
    
    @field_validator('oxygen_level', mode='before')
    @classmethod
    def validate_oxygen_level(cls, v):
        if v is not None and not isinstance(v, int):
            try:
                int(v)
            except ValueError:
                raise ValueError('Поле должно иметь целочисленный тип')
            return int(v)
        return v

    @field_validator('sugar_level', mode='before')
    @classmethod
    def validate_sugar_level(cls, v):
        if v is not None:
            if not isinstance(v, float):
                try:
                    float(v)
                except ValueError:
                    raise ValueError('Поле должно иметь вещественный тип')
            if not re.match('^[0-9]{1,2}\.[0-9]{1,2}$', str(v)):
                raise ValueError('Некорректное значение')
            return float(v)
        return v


class PageDiary(PageDiaryBase):
    """
    Модель используемая при запросе информации о странице дневника
    """
    id: uuid.UUID = Field(title='Идентификатор страницы')
    id_user: uuid.UUID
    create_date: datetime = Field(title='Дата создания страницы дневника')

    @field_validator('temperature')
    def round_temperature(cls, value):
        return round(value, 1)

    @field_validator('sugar_level')
    def round_sugar_level(cls, value):
        if value:
            return round(value, 2)


class PageDiaryOptional(PageDiaryBase):
    """
    Модель для обновления страницы дневника
    """
    @field_validator('pulse', 'upper_pressure', 'lower_pressure', mode='before')
    @classmethod
    def validate_required_integer_fields(cls, v):
        if v is None:
            raise ValueError('Поле не должно быть пустым')
        if not isinstance(v, int):
            try:
                int(v)
            except ValueError:
                raise ValueError('Поле должно иметь целочисленный тип')
        return int(v)
    
    @field_validator('temperature', mode='before')
    @classmethod
    def validate_temperature(cls, v):
        if v is None:
            raise ValueError('Поле не должно быть пустым')
        if not isinstance(v, float):
            try:
                float(v)
            except ValueError:
                raise ValueError('Поле должно иметь вещественный тип')
        if float(v) < 34.0 or float(v) > 43.0:
            raise ValueError('Некорректное значение')
        return float(v)
    
    @field_validator('oxygen_level', mode='before')
    @classmethod
    def validate_oxygen_level(cls, v):
        if v is not None and not isinstance(v, int):
            try:
                int(v)
            except ValueError:
                raise ValueError('Поле должно иметь целочисленный тип')
            return int(v)
        return v

    @field_validator('sugar_level', mode='before')
    @classmethod
    def validate_sugar_level(cls, v):
        if v is not None:
            if not isinstance(v, float):
                try:
                    float(v)
                except ValueError:
                    raise ValueError('Поле должно иметь вещественный тип')
            if not re.match('^[0-9]{1,2}\.[0-9]{1,2}$', str(v)):
                raise ValueError('Некорректное значение')
            return float(v)
        return v
