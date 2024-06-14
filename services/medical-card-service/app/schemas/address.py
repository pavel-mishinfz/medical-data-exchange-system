from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AddressBase(BaseModel):
    subject: Optional[str] = Field(title='Субъект', default=None)
    district: Optional[str] = Field(title='Район', default=None)
    locality: Optional[str] = None
    street: Optional[str] = None
    house: Optional[int] = None
    apartment: Optional[int] = Field(title='Квартира', default=None)

    class ConfigDict:
        from_attribute = True


class AddressIn(AddressBase):
    locality: str = Field(title='Город/Населенный пункт')
    street: str = Field(title='Улица')
    house: int = Field(title='Дом')

    @field_validator('locality', 'street', mode='before')
    @classmethod
    def validate_required_fields(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        return v

    @field_validator('house', mode='before')
    @classmethod
    def validate_house(cls, v):
        if v is None:
            raise ValueError('Поле не должно быть пустым')
        if not isinstance(v, int):
            try:
                int(v)
            except ValueError:
                raise ValueError('Поле должно иметь целочисленный тип')
        return int(v)

    @field_validator('apartment', mode='before')
    @classmethod
    def validate_apartment(cls, v):
        if v and not isinstance(v, int):
            try:
                int(v)
            except ValueError:
                raise ValueError('Поле должно иметь целочисленный тип')
            return int(v)
        return v


class AddressOptional(AddressBase):
    @field_validator('locality', 'street', mode='before')
    @classmethod
    def validate_required_fields(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        return v

    @field_validator('house', mode='before')
    @classmethod
    def validate_house(cls, v):
        if v is None:
            raise ValueError('Поле не должно быть пустым')
        if not isinstance(v, int):
            try:
                int(v)
            except ValueError:
                raise ValueError('Поле должно иметь целочисленный тип')
        return int(v)

    @field_validator('apartment', mode='before')
    @classmethod
    def validate_apartment(cls, v):
        if v and not isinstance(v, int):
            try:
                int(v)
            except ValueError:
                raise ValueError('Поле должно иметь целочисленный тип')
            return int(v)
        return v
