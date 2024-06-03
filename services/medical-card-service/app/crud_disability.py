import base64

from sqlalchemy.orm import Session

from cryptography.fernet import Fernet

from .database import models
from .schemas import DisabilityIn, DisabilityOptional
from . import config


cfg: config.Config = config.load_config()
CIPHER_SUITE: Fernet = Fernet(
    base64.b64decode(cfg.encrypt_key.get_secret_value())
)


def create_disability(db: Session, disability_in: DisabilityIn) -> models.Disability:
    """
    Создает новую запись инвалидности в БД
    """
    db_disability = models.Disability(
        name=CIPHER_SUITE.encrypt(disability_in.name.encode()),
        group=CIPHER_SUITE.encrypt(str(disability_in.group).encode()),
        create_date=CIPHER_SUITE.encrypt(str(disability_in.create_date).encode())
    )

    db.add(db_disability)
    db.commit()
    db.refresh(db_disability)
    return db_disability


def get_disability(
        db: Session, disability_id: int
    ) -> models.Disability | None:
    """
    Возвращает информацию о инвалидности
    """
    return db.query(models.Disability) \
            .filter(models.Disability.id == disability_id) \
            .first()


def update_disability(
        db: Session, disability_id: int, disability_optional: DisabilityOptional
    ) -> models.Disability | None:
    """
    Обновляет информацию о инвалидности
    """
    encoded_disability_data = {key: CIPHER_SUITE.encrypt(str(value).encode()) for key, value in disability_optional.model_dump(exclude_unset=True).items()}

    result = db.query(models.Disability) \
        .filter(models.Disability.id == disability_id) \
        .update(encoded_disability_data)
    db.commit()

    if result == 1:
        return get_disability(db, disability_id)
    return None


def delete_disability(
        db: Session, disability_id: int
    ) -> models.Disability | None:
    """
    Удаляет информацию о инвалидности
    """
    deleted_disability = get_disability(db, disability_id)

    result = db.query(models.Disability) \
        .filter(models.Disability.id == disability_id) \
        .delete()
    db.commit()

    if result == 1:
        return deleted_disability
    return None
