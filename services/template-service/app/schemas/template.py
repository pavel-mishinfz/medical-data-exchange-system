from pydantic import BaseModel, Field


class TemplateBase(BaseModel):
    """
    Базовая модель шаблона
    """
    name: str = Field(title='Название шаблона')
    path: str = Field(title='Путь к файлу')

    class ConfigDict:
        from_attribute = True


class Template(TemplateBase):
    """
    Модель используемая при запросе информации о шаблоне
    """
    id: int = Field(title='Идентификатор шаблона')
