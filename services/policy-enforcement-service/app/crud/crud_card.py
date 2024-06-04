import uuid
from sqlalchemy.orm import Session
from ..database import models


def get_available_pages_of_medical_card(db: Session, doctor_id: uuid.UUID):
    """
    Возвращает список медицинских карт, принадлежащие конкретному врачу
    """
    pages = (db.query(models.Pages.id)
            .filter(models.Pages.id_doctor == doctor_id)
            .all())
    return [page[0] for page in pages]