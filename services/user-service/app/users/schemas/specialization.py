from typing import Optional
from pydantic import Field, BaseModel

from .user import UserRead


class SpecializationBase(BaseModel):
    """
    Базовая модель специализации
    """
    name: Optional[str] = Field(None, title='Наименование специализации')

    class ConfigDict:
        from_attribute = True


class SpecializationIn(SpecializationBase):
    """
    Модель для добавления специализации
    """
    name: str


class Specialization(SpecializationBase):
    """
    Модель используемая при запросе информации о специализации и врачах
    """
    id: int
    name: str


class SpecializationAndDoctors(SpecializationBase):
    """
    Модель используемая при запросе информации о специализации и врачах
    """
    id: int
    name: str
    doctors: Optional[list[UserRead]] = Field(None, title='Список врачей данной специализации')


class SpecializationOptional(SpecializationBase):
    """
    Модель для обновления информации о специализации
    """
    pass
