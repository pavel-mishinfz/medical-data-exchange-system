import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, Field


class MessageDocument(BaseModel):
    """
    Базовая модель вложения
    """
    name: str
    path_to_file: str

    class ConfiDict:
        from_attribute = True
        

class MessageBase(BaseModel):
    """
    Базовая модель сообщения
    """
    message: str = Field(title='Текст сообщения')

    class ConfiDict:
        from_attribute = True


class MessageIn(MessageBase):
    """
    Модель для добавления сообщения в базу данных
    """
    chat_id: int = Field(title='Идентификатор чата')
    sender_id: uuid.UUID = Field(title='Идентификатор отправителя')


class Message(MessageBase):
    """
    Модель используемая при запросе информации о сообщении
    """
    id: uuid.UUID
    sender_id: uuid.UUID = Field(title='Идентификатор отправителя')
    documents: Optional[list[MessageDocument]] = None
    send_date: datetime.datetime
    update_date: Optional[datetime.datetime] = None


class MessageUpdate(MessageBase):
    """
    Модель для обновления сообщения
    """
    pass
