from pydantic import BaseModel, Field


class PageBase(BaseModel):
    """
    Базовая модель страницы медкарты
    """
    id_card: int = Field(title='Идентификатор медкарты')
    id_template: int = Field(title='Идентификатор шаблона')
    data: dict = Field(title='Данные страницы')

    class ConfigDict:
        from_attribute = True


class PageIn(PageBase):
    """
    Модель для добавления/обновления страницы
    """


class Page(PageBase):
    """
    Модель используемая при запросе информации о странице
    """
    id: int = Field(title='Идентификатор страницы')
