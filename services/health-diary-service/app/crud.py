from sqlalchemy.orm import Session, joinedload
from .database import models
from .schemas import PageDiaryIn


def create_diary(
        db: Session, user_id: int
    ) -> models.Diary:
    """
    Создает новый дневник здоровья в БД
    """
    db_diary = models.Diary(
        id_user=user_id,
    )

    db.add(db_diary)
    db.commit()
    db.refresh(db_diary)
    return db_diary


def get_diary(
        db: Session, diary_id: int
    ) -> models.Diary | None:
    """
    Возвращает дневник
    """
    return db.query(models.Diary) \
        .options(joinedload(models.Diary.pages)) \
        .filter(models.Diary.id == diary_id) \
        .first()


def delete_diary(
        db: Session, diary_id: int
    ) -> models.Diary | None:
    """
    Удаляет информацию о дневнике
    """
    deleted_diary = get_diary(db, diary_id)
    if deleted_diary is None:
        return None

    db.delete(deleted_diary)
    db.commit()

    return deleted_diary


def create_page(
        db: Session, diary_id: int, page_in: PageDiaryIn
    ) -> models.PageDiary:
    """
    Создает новую страницу для дневника в БД
    """
    db_page = models.PageDiary(
        id_diary=diary_id,
        pulse=page_in.pulse,
        comment=page_in.comment
    )

    db.add(db_page)
    db.commit()
    db.refresh(db_page)

    return db_page


def get_page(
        db: Session, page_id: int
    ) -> models.PageDiary | None:
    """
    Возвращает конкретную старницу дневника
    """
    return db.query(models.PageDiary) \
            .filter(models.PageDiary.id == page_id) \
            .first()


def update_page(
        db: Session, page_id: int, page_in: PageDiaryIn
    ) -> models.PageDiary | None:
    """
    Обновляет информацию о старнице
    """
    result = db.query(models.PageDiary) \
        .filter(models.PageDiary.id == page_id) \
        .update(page_in.model_dump())
    db.commit()

    if result == 1:
        return get_page(db, page_id)
    return None


def delete_page(
        db: Session, page_id: int
    ) -> models.PageDiary | None:
    """
    Удаляет информацию о странице
    """
    deleted_page = get_page(db, page_id)

    result = db.query(models.PageDiary) \
        .filter(models.PageDiary.id == page_id) \
        .delete()
    db.commit()

    if result == 1:
        return deleted_page
    return None
