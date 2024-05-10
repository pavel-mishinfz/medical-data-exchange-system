from pydantic import BaseModel, Field


class Busyness(BaseModel):
    id: int = Field(title='Идентификатор')
    name: str = Field(title='Тип занятости')

    class ConfigDict:
        from_attribute = True
