from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class DisabilityBase(BaseModel):
    name: Optional[str] = None
    group: Optional[int] = None
    create_date: Optional[date] = None

    class ConfigDict:
        from_attribute = True


class DisabilityIn(DisabilityBase):
    name: str = Field(title='Наименование')
    group: int = Field(title='Группа')
    create_date: date = Field(title='Дата установления инвалидности')


class DisabilityOptional(DisabilityBase):
    pass
