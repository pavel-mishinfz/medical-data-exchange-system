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
    pass


class Page(PageBase):
    """
    Модель используемая при запросе информации о странице
    """
    id: int = Field(title='Идентификатор страницы')
    id_template: int = Field(title='Идентификатор шаблона страницы')
    create_date: datetime = Field(title='Дата создания страницы')
    documents: Optional[list[Document]] = Field(None, title='Документы страницы')


class PageShortOut(BaseModel):
    """
    Модель используемая при запросе информации об идентификаторе страницы
    """
    id: int = Field(title='Идентификатор страницы')

    class ConfigDict:
        from_attribute = True
