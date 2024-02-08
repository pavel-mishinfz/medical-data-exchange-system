import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload
from .database import models
from .schemas import PageIn, CardIn


def create_card(
        db: Session, user_id: uuid.UUID, card_in: CardIn
    ) -> models.Card:
    """
    Создает новую медкарту в БД
    """
    db_card = models.Card(
        id_user=user_id,
        user_name=card_in.user_name,
        create_date=datetime.now(timezone.utc)
    )

    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


def get_card(
        db: Session, card_id: int
    ) -> models.Card | None:
    """
    Возвращает медкарту
    """
    return db.query(models.Card) \
        .filter(models.Card.id == card_id) \
        .first()


def get_card_with_pages(
        db: Session, card_id: int
    ) -> tuple[models.Card | None, list[models.Page] | None]:
    """
    Возвращает медкарту
    """
    card = get_card(db, card_id)
    pages = db.query(models.Page) \
        .order_by(models.Page.id) \
        .filter(models.Page.id_card == card_id) \
        .all()
    return card, pages


def update_card(
        db: Session, card_id: int, card_in: CardIn
    ) -> models.Card | None:
    """
    Обновляет информацию о медкарте
    """
    result = db.query(models.Card) \
        .filter(models.Card.id == card_id) \
        .update(card_in.model_dump())
    db.commit()

    if result == 1:
        return get_card(db, card_id)
    return None


def delete_card(
        db: Session, card_id: int
    ) -> models.Card | None:
    """
    Удаляет информацию о медкарте
    """
    deleted_card = get_card(db, card_id)
    if deleted_card is None:
        return None

    db.delete(deleted_card)
    db.commit()

    return deleted_card


def create_page(
        db: Session, card_id: int, template_id: int, page_in: PageIn
    ) -> models.Page:
    """
    Создает новую страницу для медкарты в БД
    """
    db_page = models.Page(
        id_card=card_id,
        id_template=template_id,
        data=page_in.data,
        create_date=datetime.now(timezone.utc)
    )

    db.add(db_page)
    db.commit()
    db.refresh(db_page)

    return db_page


def get_page(
        db: Session, page_id: int
    ) -> models.Page | None:
    """
    Возвращает конкретную старницу медкарты
    """
    return db.query(models.Page) \
            .filter(models.Page.id == page_id) \
            .first()


def update_page(
        db: Session, page_id: int, page_in: PageIn
    ) -> models.Page | None:
    """
    Обновляет информацию о старнице
    """
    result = db.query(models.Page) \
        .filter(models.Page.id == page_id) \
        .update(page_in.model_dump())
    db.commit()

    if result == 1:
        return get_page(db, page_id)
    return None


def delete_page(
        db: Session, page_id: int
    ) -> models.Page | None:
    """
    Удаляет информацию о странице
    """
    deleted_page = get_page(db, page_id)

    result = db.query(models.Page) \
        .filter(models.Page.id == page_id) \
        .delete()
    db.commit()

    if result == 1:
        return deleted_page
    return None
