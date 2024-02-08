from pydantic import BaseModel, Field


class DiaryBase(BaseModel):
    """
    Базовая модель дневника здоровья
    """

    class ConfigDict:
        from_attribute = True


class DiaryIn(DiaryBase):
    """
    Модель для добавления/обновления дневника
    """


class Diary(DiaryBase):
    """
    Модель используемая при запросе информации о дневнике
    """
    id: int = Field(title='Идентификатор дневника')

