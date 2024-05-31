import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import or_

from .database import models
from .schemas import PageIn, PageUpdate, CardIn, CardOptional, DisabilityIn

from . import crud_address
from . import crud_passport
from . import crud_disability


def create_card(
        db: Session, card_in: CardIn
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
        id_user=card_in.id_user,
        name=card_in.name,
        surname=card_in.surname,
        patronymic=card_in.patronymic,
        is_man=card_in.is_man,
        birthday=card_in.birthday,
        id_address=address.id,
        phone=card_in.phone,
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
        db: Session, card_id: int | None = None, user_id: uuid.UUID | None = None
    ) -> models.Card | None:
    """
    Возвращает медкарту
    """
    return db.query(models.Card)\
        .filter(
            or_(
                models.Card.id == card_id, 
                models.Card.id_user == user_id)
            ) \
        .filter(models.Card.is_deleted == False) \
        .first()


def get_cards_list(
        db: Session
    ) -> list[models.Card]:
    """
    Возвращает список медкарт
    """
    return db.query(models.Card).filter(models.Card.is_deleted == False).all()


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
        if None in dict(card_optional.disability).values():
            crud_disability.delete_disability(db, id_disability)
            id_disability = None
        else:
            disability = crud_disability.update_disability(db, id_disability, card_optional.disability)
            if disability is None:
                disability = crud_disability.create_disability(db, DisabilityIn(
                    name=card_optional.disability.name, 
                    group=card_optional.disability.group, 
                    create_date=card_optional.disability.create_date)
                    )
            id_disability = disability.id

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
    ) -> bool:
    """
    Удаляет информацию о медкарте
    """
    deleted_card = get_card(db, card_id)
    if deleted_card is None:
        return False

    deleted_card.is_deleted = True
    db.add(deleted_card)
    db.commit()

    return deleted_card.is_deleted


def create_page(
        db: Session, card_id: int, template_id: int, page_in: PageIn
    ) -> models.Page:
    """
    Создает новую страницу для медкарты в БД
    """
    db_page = models.Page(
        id_card=card_id,
        id_template=template_id,
        id_doctor=page_in.id_doctor,
        data=page_in.data,
        create_date=datetime.now(timezone.utc)
    )

    db.add(db_page)
    db.commit()
    db.refresh(db_page)

    return db_page


def get_page(
        db: Session, page_id: uuid.UUID
    ) -> models.Page | None:
    """
    Возвращает конкретную старницу медкарты
    """
    return db.query(models.Page) \
            .filter(models.Page.id == page_id) \
            .filter(models.Page.is_deleted == False) \
            .first()


def get_pages(
        db: Session, card_id: int
    ) -> list[models.Page] | None:
    """
    Возвращает медкарту
    """
    return db.query(models.Page) \
        .filter(models.Page.id_card == card_id) \
        .filter(models.Page.is_deleted == False) \
        .order_by(models.Page.create_date.asc()) \
        .all()


def update_page(
        db: Session, page_id: uuid.UUID, page_update: PageUpdate
    ) -> models.Page | None:
    """
    Обновляет информацию о старнице
    """
    result = db.query(models.Page) \
        .filter(models.Page.id == page_id) \
        .update(page_update.model_dump())
    db.commit()

    if result == 1:
        return get_page(db, page_id)
    return None


def delete_page(
        db: Session, page_id: uuid.UUID
    ) -> tuple[bool, models.Document] | tuple[False, None]:
    """
    Удаляет информацию о странице
    """
    deleted_page = get_page(db, page_id)
    if deleted_page:
        documents = deleted_page.documents
        deleted_page.is_deleted = True
        db.add(deleted_page)
        db.commit()
        return deleted_page.is_deleted, documents
    return False, None


def get_list_family_status(
        db: Session
    ) -> list[models.FamilyStatus]:
    """
    Возвращает список доступных семейных статусов
    """
    return db.query(models.FamilyStatus).all()


def get_list_education(
        db: Session
    ) -> list[models.Education]:
    """
    Возвращает список доступных типов образования
    """
    return db.query(models.Education).all()


def get_list_busyness(
        db: Session
    ) -> list[models.Busyness]:
    """
    Возвращает информацию о типе занятости
    """
    return db.query(models.Busyness).all()
