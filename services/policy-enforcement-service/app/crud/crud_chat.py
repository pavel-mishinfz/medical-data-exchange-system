import uuid
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..database import models


def get_available_chats(db: Session, user_id: uuid.UUID):
    """
    Возвращает список идентификаторов чатов
    """
    chats = (db.query(models.Chats.id)
            .filter(
                or_(
                    models.Chats.doctor_id == user_id,
                    models.Chats.patient_id == user_id
                )
            )
            .all())
    return [chat[0] for chat in chats]