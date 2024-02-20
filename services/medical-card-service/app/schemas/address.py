from typing import Optional

from pydantic import BaseModel, Field


class AddressBase(BaseModel):
    subject: Optional[str] = Field(title='Субъект', default=None)
    district: Optional[str] = Field(title='Район', default=None)
    locality: Optional[str] = None
    street: Optional[str] = None
    house: Optional[int] = None
    apartment: Optional[int] = Field(title='Квартира', default=None)
    phone: Optional[str] = None

    class ConfigDict:
        from_attribute = True


class AddressIn(AddressBase):
    locality: str = Field(title='Город/Населенный пункт')
    street: str = Field(title='Улица')
    house: int = Field(title='Дом')
    phone: str = Field(title='Номер телефона', min_length=11, max_length=12)


class AddressOptional(AddressBase):
    pass
