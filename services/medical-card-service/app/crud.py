import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from .database import models
from .schemas import PageIn, CardIn, CardOptional

from . import crud_address
from . import crud_passport
from . import crud_disability


def create_card(
        db: Session, user_id: uuid.UUID, card_in: CardIn
    ) -> models.Card:
    """
    Создает новую медкарту в БД
    """
    address = crud_address.create_address(db, card_in.address)
    passport = crud_passport.create_passport(db, card_in.passport)

    id_disability = None
    if card_in.disability:
        disability = crud_disability.create_disability(db, card_in.disability)
        id_disability = disability.id

    db_card = models.Card(
        id_user=user_id,
        first_name=card_in.first_name,
        surname=card_in.surname,
        last_name=card_in.last_name,
        is_man=card_in.is_man,
        birthday_date=card_in.birthday_date,
        id_address=address.id,
        is_urban_area=card_in.is_urban_area,
        number_policy=card_in.number_policy,
        snils=card_in.snils,
        insurance_company=card_in.insurance_company,
        benefit_category_code=card_in.benefit_category_code,
        id_passport=passport.id,
        id_family_status=card_in.id_family_status,
        id_education=card_in.id_education,
        id_busyness=card_in.id_busyness,
        id_disability=id_disability,
        workplace=card_in.workplace,
        job=card_in.job,
        blood_type=card_in.blood_type,
        rh_factor_is_pos=card_in.rh_factor_is_pos,
        allergy=card_in.allergy,
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
    Возвращает медкарту cо всеми страницами
    """
    card = get_card(db, card_id)
    pages = get_pages(db, card_id)
    return card, pages


def update_card(
        db: Session, card_id: int, card_optional: CardOptional
    ) -> models.Card | None:
    """
    Обновляет информацию о медкарте
    """
    exclude_fields = {
        'address',
        'passport',
        'disability'
    }

    before_update_card = get_card(db, card_id)
    id_address = before_update_card.id_address
    id_passport = before_update_card.id_passport
    id_disability = before_update_card.id_disability

    if card_optional.address:
        updated_address = crud_address.update_address(db, id_address, card_optional.address)
        id_address = updated_address.id
    if card_optional.passport:
        updated_passport = crud_passport.update_passport(db, id_passport, card_optional.passport)
        id_passport = updated_passport.id
    if card_optional.disability:
        updated_disability = crud_disability.update_disability(db, id_disability, card_optional.disability)
        id_disability = updated_disability.id

    force_update_fields = {
        'id_address': id_address,
        'id_passport': id_passport,
        'id_disability': id_disability
    }
    result = db.query(models.Card) \
        .filter(models.Card.id == card_id) \
        .update(card_optional.model_dump(exclude=exclude_fields, exclude_unset=True) | force_update_fields)
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


def get_pages(
        db: Session, card_id: int
    ) -> list[models.Page] | None:
    """
    Возвращает медкарту
    """
    return db.query(models.Page) \
        .filter(models.Page.id_card == card_id) \
        .order_by(models.Page.id) \
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
    ) -> tuple[models.Page, models.Document] | tuple[None, None]:
    """
    Удаляет информацию о странице
    """
    deleted_page = get_page(db, page_id)
    if deleted_page:
        documents = deleted_page.documents
        db.delete(deleted_page)
        db.commit()
        return deleted_page, documents
    return None, None
