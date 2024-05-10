from pydantic import BaseModel, Field


class TemplateBase(BaseModel):
    """
    Базовая модель шаблона
    """
    name: str = Field(title='Название шаблона')
    structure: list[dict] = Field(title='Поля страницы шаблона', default=[
        {
            "title": "",
            "divider": "",
            "body": "",
            "fields": [
                {
                    "title": None,
                    "type": "",
                    "name": "",
                    "value": ""
                }
            ]
        }
    ])

    class ConfigDict:
        from_attribute = True


class Template(TemplateBase):
    """
    Модель используемая при запросе информации о шаблоне
    """
    id: int = Field(title='Идентификатор шаблона')


class TemplateIn(TemplateBase):
    """
    Модель для добавления/обновления шаблона
    """
    pass
