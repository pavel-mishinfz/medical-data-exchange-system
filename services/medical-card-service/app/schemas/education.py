from pydantic import BaseModel, Field


class Education(BaseModel):
    id: int = Field(title='Идентификатор')
    name: str = Field(title='Тип образование')

    class ConfigDict:
        from_attribute = True
