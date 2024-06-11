from sqlalchemy.orm import Session
from ..database import models


def get_meeting(db: Session, meeting_id: int):
    """
    Возвращает информацию о встрече
    """
    return (db.query(models.Meetings)
            .filter(models.Meetings.meeting_id == meeting_id)
            .frist())