from pydantic import BaseModel, Field, model_validator


class CardBase(BaseModel):
    """
    Базовая модель медкарты
    """
    user_name: str = Field(title='ФИО пациента')

    class ConfigDict:
        from_attribute = True


class CardIn(CardBase):
    """
    Модель для добавления/обновления медкарты
    """


class Card(CardBase):
    """
    Модель используемая при запросе информации о медкарте
    """
    id: int = Field(title='Идентификатор медкарты')
