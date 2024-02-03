from pydantic import BaseModel, Field


class EmailBody(BaseModel):
    to: str = Field(title='Адрес получателя')
    subject: str = Field(title='Тема сообщения')
    message: str = Field(title='Текст сообщения')
