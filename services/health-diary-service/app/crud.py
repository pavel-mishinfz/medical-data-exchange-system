import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from .database import models
from .schemas import PageDiaryIn


def create_page_diary(
        db: Session, user_id: uuid.UUID, page_diary_in: PageDiaryIn
    ) -> models.PageDiary:
    """
    Создает новую страницу дневника здоровья в БД
    """
    db_page_diary = models.PageDiary(
        id_user=user_id,
        pulse=page_diary_in.pulse,
        comment=page_diary_in.comment,
        create_date=datetime.now(timezone.utc)
    )

    db.add(db_page_diary)
    db.commit()
    db.refresh(db_page_diary)
    return db_page_diary


def get_page_diary(
        db: Session, page_diary_id: int
    ) -> models.PageDiary | None:
    """
    Возвращает страницу дневника
    """
    return db.query(models.PageDiary) \
        .filter(models.PageDiary.id == page_diary_id) \
        .first()


def get_page_diary_list(
        db: Session, user_id: uuid.UUID
    ) -> list[models.PageDiary] | None:
    """
    Возвращает все страницы дневника пользователя
    """
    return db.query(models.PageDiary) \
        .filter(models.PageDiary.id_user == user_id) \
        .all()


def update_page_diary(
        db: Session, page_diary_id: int, page_diary_in: PageDiaryIn
    ) -> models.PageDiary | None:
    """
    Обновляет информацию о старнице
    """
    result = db.query(models.PageDiary) \
        .filter(models.PageDiary.id == page_diary_id) \
        .update(page_diary_in.model_dump())
    db.commit()

    if result == 1:
        return get_page_diary(db, page_diary_id)
    return None


def delete_page_diary(
        db: Session, page_diary_id: int
    ) -> models.PageDiary | None:
    """
    Удаляет информацию о странице дневнике
    """
    deleted_page_diary = get_page_diary(db, page_diary_id)
    if deleted_page_diary is None:
        return None

    db.delete(deleted_page_diary)
    db.commit()

    return deleted_page_diary
