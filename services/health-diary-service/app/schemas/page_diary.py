from datetime import datetime
from decimal import Decimal
from typing import Optional, Annotated
import uuid

from pydantic import BaseModel, Field, field_validator


class PageDiaryBase(BaseModel):
    """
    Базовая модель страницы дневника здоровья
    """
    pulse: Optional[int] = None
    temperature: Annotated[
                     Decimal, Field(None, title='Показатель температуры', decimal_places=1)
                 ] | None = None
    upper_pressure: Optional[int] = None
    lower_pressure: Optional[int] = None
    oxygen_level: Optional[int] = Field(None, title='Показатель кислорода в крови')
    sugar_level: Annotated[
                     Decimal, Field(None, title='Показатель сахара в крови', decimal_places=2)
                 ] | None = None
    comment: Optional[str] = Field(None, title='Комментарий о своем здоровье')

    class ConfigDict:
        from_attribute = True


class PageDiaryIn(PageDiaryBase):
    """
    Модель для добавления страницы дневника
    """
    pulse: int = Field(title='Показатель пульса')
    temperature: Annotated[Decimal, Field(title='Показатель температуры', decimal_places=1)]
    upper_pressure: int = Field(title='Показатель верхнего артериального давления')
    lower_pressure: int = Field(title='Показатель нижнего артериального давления')


class PageDiary(PageDiaryBase):
    """
    Модель используемая при запросе информации о странице дневника
    """
    id: uuid.UUID = Field(title='Идентификатор страницы')
    create_date: datetime = Field(title='Дата создания страницы дневника')

    @field_validator('temperature', 'sugar_level')
    def make_float_from_str(cls, value):
        if value:
            return float(value)


class PageDiaryOptional(PageDiaryBase):
    """
    Модель для обновления страницы дневника
    """
    pass
