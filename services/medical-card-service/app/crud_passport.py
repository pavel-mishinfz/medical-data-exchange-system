import base64

from sqlalchemy.orm import Session

from cryptography.fernet import Fernet

from .database import models
from .schemas import PassportIn, PassportOptional
from . import config


cfg: config.Config = config.load_config()
CIPHER_SUITE: Fernet = Fernet(
    base64.b64decode(cfg.encrypt_key.get_secret_value())
)


def create_passport(db: Session, passport: PassportIn) -> models.Passport:
    """
    Создает новую запись паспорта в БД
    """
    db_passport = models.Passport(
        series=CIPHER_SUITE.encrypt(passport.series.encode()),
        number=CIPHER_SUITE.encrypt(passport.number.encode())
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
    encoded_passport_data = {key: CIPHER_SUITE.encrypt(value.encode()) for key, value in passport_optional.model_dump(exclude_unset=True).items()}

    result = db.query(models.Passport) \
        .filter(models.Passport.id == passport_id) \
        .update(encoded_passport_data)
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
