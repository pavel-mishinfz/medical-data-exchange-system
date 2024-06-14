from typing import Optional, List, Dict
from pydantic import BaseModel, Field, field_validator, model_validator


class FieldItem(BaseModel):
    title: Optional[str]
    type: str
    name: str
    value: Optional[str]
    options: Optional[List[Dict]] = None

    @model_validator(mode='before')
    def check_select_type_options(cls, values):
        if values.get('type') == 'select':
            options = values.get('options')
            if not options:
                raise ValueError('Поле <Значения списка> обязательно для типа <Поле выбора>')
            if not isinstance(options, list):
                raise ValueError('Поле options должно быть списком словарей')
            for option in options:
                if 'id' not in option or 'name' not in option:
                    raise ValueError('Каждый словарь в options должен содержать поля id и name')
                if not option['name']:
                    raise ValueError('Поле <Значения списка> должно быть заполнено')
        return values
    

class StructureItem(BaseModel):
    """
    Базовая модель структуры шаблона
    """
    title: str
    divider: Optional[str]
    body: Optional[str]
    fields: List[FieldItem]


class TemplateBase(BaseModel):
    """
    Базовая модель шаблона
    """
    name: str = Field(title='Название шаблона')
    structure: List[StructureItem] = Field(title='Поля страницы шаблона')

    class ConfigDict:
        from_attribute = True


class Template(TemplateBase):
    """
    Модель используемая при запросе информации о шаблоне
    """
    id: int = Field(title='Идентификатор шаблона')
    is_deleted: bool


class TemplateIn(TemplateBase):
    """
    Модель для добавления/обновления шаблона
    """
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is None or not v.strip():
            raise ValueError('Поле не должно быть пустым')
        return v

    @model_validator(mode='before')
    def validate_structure(cls, values):
        structure = values.get('structure', [])
        names = set()

        for item in structure:
            if not item['title']:
                raise ValueError('Поле <Заголовок> не должно быть пустым')

            if item['divider'] and len(item['divider']) > 1:
                raise ValueError('Поле <Разделитель> должно содержать не более одного символа')
            
            for field in item['fields']:
                if not field['name']:
                    raise ValueError('Поле <Идентификатор> не должно быть пустым')
                if field['name'] in names:
                    raise ValueError(f'Поле <Идентификатор> должно быть уникально')
                names.add(field['name'])
        
        return values
    
