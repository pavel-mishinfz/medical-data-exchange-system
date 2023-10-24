from pydantic import BaseModel, Field


class TemplateBase(BaseModel):
    id: int = Field(title='Идентификатор шаблона')
    name: str = Field(title='Название шаблона')


class Template(TemplateBase):
    path: str = Field(title='Путь к файлу')
