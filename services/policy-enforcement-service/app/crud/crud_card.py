import uuid
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..database import models


def get_available_pages_of_medical_card(db: Session, doctor_id: uuid.UUID):
    """
    Возвращает список идентификаторов страниц медицинских карт, принадлежащие конкретному врачу
    """
    pages = (db.query(models.Pages.id)
            .filter(models.Pages.id_doctor == doctor_id)
            .all())
    return [page[0] for page in pages]


def get_available_pages_of_health_diary(db: Session, user_id: uuid.UUID):
    """
    Возвращает список идентификаторов страниц дневника здоровья, принадлежащие конкретному пользователю
    """
    pages = (db.query(models.Diaries.id)
            .filter(models.Diaries.id_user == user_id)
            .all())
    return [page[0] for page in pages]


def get_card(db: Session, card_id: int):
    """
    Возвращает информацию о медкарте
    """
    return (db.query(models.Cards)
            .filter(models.Cards.id == card_id)
            .first())
