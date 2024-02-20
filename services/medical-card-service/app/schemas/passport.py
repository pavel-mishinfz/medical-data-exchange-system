from typing import Optional

from pydantic import BaseModel, Field


class PassportBase(BaseModel):
    series: Optional[str] = None
    number: Optional[str] = None

    class ConfigDict:
        from_attribute = True


class PassportIn(PassportBase):
    series: str = Field(title='Серия', min_length=4, max_length=4)
    number: str = Field(title='Номер', min_length=6, max_length=6)


class PassportOptional(PassportBase):
    pass
