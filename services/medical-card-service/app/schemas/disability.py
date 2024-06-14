from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class DisabilityBase(BaseModel):
    name: Optional[str] = None
    group: Optional[int] = None
    create_date: Optional[date] = None

    class ConfigDict:
        from_attribute = True


class DisabilityIn(DisabilityBase):
    @model_validator(mode='before')
    def check_all_or_none(cls, values):
        if isinstance(values, dict):
            name, group, create_date = values.get('name'), values.get('group'), values.get('create_date')
            filled_fields = [name, group, create_date]
            if any(filled_fields) and not all(filled_fields):
                raise ValueError('Все поля должны быть заполнены')
        return values

    @field_validator('name', mode='before')
    @classmethod
    def validate_name(cls, v):
        if v and not v.strip():
            raise ValueError('Поле не должно быть пустым')
        return v

    @field_validator('group', mode='before')
    @classmethod
    def validate_group(cls, v):
        if v and not isinstance(v, int):
            try:
                int(v)
            except ValueError:
                raise ValueError('Поле должно иметь целочисленный тип')
            return int(v)
        return v

    @field_validator('create_date', mode='before')
    @classmethod
    def validate_create_date(cls, v):
        if not isinstance(v, date):
            try:
                parsed_date = datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError('Поле должно иметь формат даты')
            if parsed_date > date.today():
                raise ValueError('Дата не может быть больше текущей')
        return v


class DisabilityOptional(DisabilityBase):
    @model_validator(mode='before')
    def check_all_or_none(cls, values):
        if isinstance(values, dict):
            name, group, create_date = values.get('name'), values.get('group'), values.get('create_date')
            filled_fields = [name, group, create_date]
            if any(filled_fields) and not all(filled_fields):
                raise ValueError('Все поля должны быть заполнены')
        return values

    @field_validator('name', mode='before')
    @classmethod
    def validate_name(cls, v):
        if v and not v.strip():
            raise ValueError('Поле не должно быть пустым')
        return v

    @field_validator('group', mode='before')
    @classmethod
    def validate_group(cls, v):
        if v and not isinstance(v, int):
            try:
                int(v)
            except ValueError:
                raise ValueError('Поле должно иметь целочисленный тип')
            return int(v)
        return v

    @field_validator('create_date', mode='before')
    @classmethod
    def validate_create_date(cls, v):
        if not isinstance(v, date):
            try:
                parsed_date = datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError('Поле должно иметь формат даты')
            if parsed_date > date.today():
                raise ValueError('Дата не может быть больше текущей')
        return v
