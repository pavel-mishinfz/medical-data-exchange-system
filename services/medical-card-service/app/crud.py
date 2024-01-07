from sqlalchemy.orm import Session
from .database import models
from .schemas import PageIn, CardIn


def create_card(
        db: Session, card_in: CardIn
    ) -> models.Card:
    """
    Создает новую медкарту в БД
    """
    db_card = models.Card(
        id_user=card_in.id_user,
        user_name=card_in.user_name,
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
    result = db.query(models.Card) \
            .filter(models.Card.id == card_id) \
            .delete()
    db.commit()

    if result == 1:
        return deleted_card
    return None


def create_page(
        db: Session, page_in: PageIn
    ) -> models.Page:
    """
    Создает новую страницу для медкарты в БД
    """
    db_page = models.Page(
        id_card=page_in.id_card,
        id_template=page_in.id_template,
        data=page_in.data
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


def get_pages(
        db: Session, card_id: int
    ) -> list[models.Page] | None:
    """
    Возвращает все старницы медкарты
    """
    return db.query(models.Page) \
            .filter(models.Page.id_card == card_id) \
            .all()


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


def delete_pages(
        db: Session, card_id: int
    ) -> list[models.Page] | None:
    """
    Удаляет информацию о всех страницах
    """
    deleted_pages = get_pages(db, card_id)

    result = db.query(models.Page) \
        .filter(models.Page.id_card == card_id) \
        .delete()
    db.commit()

    if result == 1:
        return deleted_pages
    return None
