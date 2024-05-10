import uuid

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .document import Document


class PageBase(BaseModel):
    """
    Базовая модель страницы медкарты
    """
    data: dict = Field(title='Данные страницы')

    class ConfigDict:
        from_attribute = True


class PageIn(PageBase):
    """
    Модель для добавления страницы
    """
    id_doctor: uuid.UUID


class PageUpdate(PageBase):
    """
    Модель для обновления страницы
    """
    pass


class Page(PageBase):
    """
    Модель используемая при запросе информации о странице
    """
    id: uuid.UUID = Field(title='Идентификатор страницы')
    id_template: int = Field(title='Идентификатор шаблона страницы')
    id_doctor: uuid.UUID
    create_date: datetime = Field(title='Дата создания страницы')
    documents: Optional[list[Document]] = Field(None, title='Документы страницы')
