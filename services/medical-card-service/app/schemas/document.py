import json, uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class DocumentBase(BaseModel):
    """
    Базовая модель медицинского документа
    """
    name: Optional[str] = None
    description: Optional[str] = Field(None, title='Описание документа')

    class ConfigDict:
        from_attribute = True


class DocumentIn(DocumentBase):
    """
    Модель для добавления меддокумента
    """
    name: str = Field(title='Название документа')
    id_page: uuid.UUID = Field(title='Идентификатор страницы, к которой прикреплен документ')

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
    id: int = Field(title='Идентификатор документа')
    id_page: uuid.UUID
    path_to_file: str = Field(title='Путь до файла меддокумента')
    create_date: datetime = Field(title='Дата создания меддокумента')


class DocumentOptional(DocumentBase):
    """
    Модель для обновления меддокумента
    """
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
