from pydantic import BaseModel, Field


class FamilyStatus(BaseModel):
    id: int = Field(title='Идентификатор')
    name: str = Field(title='Статус семейного положения')

    class ConfigDict:
        from_attribute = True
