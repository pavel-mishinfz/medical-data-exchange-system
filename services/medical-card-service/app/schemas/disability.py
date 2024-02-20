from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DisabilityBase(BaseModel):
    name: Optional[str] = None
    group: Optional[int] = None
    date: Optional[datetime] = None

    class ConfigDict:
        from_attribute = True


class DisabilityIn(DisabilityBase):
    name: str = Field(title='Наименование')
    group: int = Field(title='Группа')
    date: datetime = Field(title='Дата установления инвалидности')


class DisabilityOptional(DisabilityBase):
    pass
