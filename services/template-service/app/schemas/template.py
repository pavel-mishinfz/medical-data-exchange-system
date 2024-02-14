import json

from pydantic import BaseModel, Field, model_validator


class TemplateBase(BaseModel):
    """
    Базовая модель шаблона
    """
    name: str = Field(title='Название шаблона')

    class ConfigDict:
        from_attribute = True


class TemplateOut(TemplateBase):
    """
    Модель используемая при запросе информации о шаблоне для пользователя
    """
    id: int = Field(title='Идентификатор шаблона')


class Template(TemplateOut):
    """
    Модель используемая при запросе информации о шаблоне
    """
    path_to_file: str = Field(title='Путь к файлу')


class TemplateIn(TemplateBase):
    """
    Модель для добавления/обновления шаблона
    """
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
