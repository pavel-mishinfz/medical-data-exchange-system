import uuid
from sqlalchemy.orm import Session
from ..database import models


def get_available_messages(db: Session, user_id: uuid.UUID):
    """
    Возвращает список идентификаторов сообщений
    """
    messages = (db.query(models.Messages.id)
            .filter(models.Messages.sender_id == user_id)
            .all())
    return [msg[0] for msg in messages]
