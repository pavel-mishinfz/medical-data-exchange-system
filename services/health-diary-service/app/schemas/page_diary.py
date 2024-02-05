from typing import Optional

from pydantic import BaseModel, Field


class PageDiaryBase(BaseModel):
    """
    Базовая модель страницы дневника здоровья
    """
    pulse: int = Field(title='Показатель пульса пациента')
    comment: Optional[str] = Field(title='Комментарий пациента о своем здоровье', default=None)

    class ConfigDict:
        from_attribute = True


class PageDiaryIn(PageDiaryBase):
    """
    Модель для добавления/обновления страницы
    """


class PageDiary(PageDiaryBase):
    """
    Модель используемая при запросе информации о странице
    """
    id: int = Field(title='Идентификатор страницы')
