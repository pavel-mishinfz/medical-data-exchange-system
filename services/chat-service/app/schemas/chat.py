import uuid
from pydantic import BaseModel, Field


class ChatBase(BaseModel):
    """
    Базовая модель чата
    """
    doctor_id: uuid.UUID = Field(title='Идентификатор врача')
    patient_id: uuid.UUID = Field(title='Идентификатор пациента')

    class ConfiDict:
        from_attribute = True


class ChatIn(ChatBase):
    """
    Модель для добавления чата в базу данных
    """
    pass


class Chat(ChatBase):
    """
    Модель используемая при запросе информации о чате
    """
    id: int
    