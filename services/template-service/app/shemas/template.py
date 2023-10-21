from pydantic import BaseModel, Field


class Template(BaseModel):
    id: int = Field(title='Идентификатор шаблона')
    name: str = Field(title='Название шаблона')
    path: str = Field(title='Путь к файлу')
