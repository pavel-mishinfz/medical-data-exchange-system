from typing import Optional
from pydantic import Field, BaseModel


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
    img: str


class SpecializationUpsert(SpecializationBase):
    """
    Модель для добавления/обновления специализации
    """
    id: int
    name: str
    img: str


class SpecializationOptional(SpecializationBase):
    """
    Модель для обновления информации о специализации
    """
    pass
