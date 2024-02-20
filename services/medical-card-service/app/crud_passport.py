from sqlalchemy.orm import Session

from .database import models
from .schemas import PassportIn, PassportOptional


def create_passport(db: Session, passport: PassportIn) -> models.Passport:
    """
    Создает новую запись паспорта в БД
    """
    db_passport = models.Passport(
        series=passport.series,
        number=passport.number
    )

    db.add(db_passport)
    db.commit()
    db.refresh(db_passport)
    return db_passport


def get_passport(
        db: Session, passport_id: int
    ) -> models.Passport | None:
    """
    Возвращает информацию о паспорте
    """
    return db.query(models.Passport) \
            .filter(models.Passport.id == passport_id) \
            .first()


def update_passport(
        db: Session, passport_id: int, passport_optional: PassportOptional
    ) -> models.Passport | None:
    """
    Обновляет информацию о паспорте
    """
    result = db.query(models.Passport) \
        .filter(models.Passport.id == passport_id) \
        .update(passport_optional.model_dump(exclude_unset=True))
    db.commit()

    if result == 1:
        return get_passport(db, passport_id)
    return None


def delete_passport(
        db: Session, passport_id: int
    ) -> models.Passport | None:
    """
    Удаляет информацию о паспорте
    """
    deleted_passport = get_passport(db, passport_id)

    result = db.query(models.Passport) \
        .filter(models.Passport.id == passport_id) \
        .delete()
    db.commit()

    if result == 1:
        return deleted_passport
    return None
