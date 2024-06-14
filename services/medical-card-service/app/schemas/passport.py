import re

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PassportBase(BaseModel):
    series: Optional[str] = None
    number: Optional[str] = None

    class ConfigDict:
        from_attribute = True


class PassportIn(PassportBase):
    series: str = Field(title='Серия')
    number: str = Field(title='Номер')

    @field_validator('series', mode='before')
    @classmethod
    def validate_series(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        if not re.match('^[0-9]{4}$', str(v)):
            raise ValueError('Значение должно быть длиной четыре цифры')
        return v

    @field_validator('number', mode='before')
    @classmethod
    def validate_number(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        if not re.match('^[0-9]{6}$', str(v)):
            raise ValueError('Значение должно быть длиной шесть цифр')
        return v


class PassportOptional(PassportBase):
    @field_validator('series', mode='before')
    @classmethod
    def validate_series(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        if not re.match('^[0-9]{4}$', str(v)):
            raise ValueError('Значение должно быть длиной четыре цифры')
        return v

    @field_validator('number', mode='before')
    @classmethod
    def validate_number(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        if not re.match('^[0-9]{6}$', str(v)):
            raise ValueError('Значение должно быть длиной шесть цифр')
        return v
