import json
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class DocumentBase(BaseModel):
    """
    Базовая модель медицинского документа
    """
    name: str = Field(title='Название документа')
    description: Optional[str] = Field(title='Описание документа', default=None)

    class ConfigDict:
        from_attribute = True


class DocumentIn(DocumentBase):
    """
    Модель для добавления/обновления меддокумента
    """
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class Document(DocumentBase):
    """
    Модель используемая при запросе информации о меддокументе
    """
    id: int = Field(title='Идентификатор медкарты')
    id_page: int = Field(title='Идентификатор страницы, к которой прикреплен документ')
    id_template: int = Field(title='Идентификатор страницы шаблона')
    path_to_file: str = Field(title='Путь до файла меддокумента')
    create_date: datetime = Field(title='Дата создания меддокумента')
