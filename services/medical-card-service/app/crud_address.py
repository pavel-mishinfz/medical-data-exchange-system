import base64

from sqlalchemy.orm import Session

from cryptography.fernet import Fernet

from .database import models
from .schemas import AddressIn, AddressOptional
from . import config


cfg: config.Config = config.load_config()
CIPHER_SUITE: Fernet = Fernet(
    base64.b64decode(cfg.encrypt_key.get_secret_value())
)


def create_address(db: Session, address_in: AddressIn) -> models.Address:
    """
    Создает новую запись адреса в БД
    """
    encoded_subject = None
    encoded_district = None
    encoded_apartment = None
    if address_in.subject:
        encoded_subject = CIPHER_SUITE.encrypt(address_in.subject.encode())
    if address_in.district:
        encoded_district = CIPHER_SUITE.encrypt(address_in.district.encode())
    if address_in.apartment:
        encoded_apartment = CIPHER_SUITE.encrypt(str(address_in.apartment).encode())

    db_address = models.Address(
        subject=encoded_subject,
        district=encoded_district,
        locality=CIPHER_SUITE.encrypt(address_in.locality.encode()),
        street=CIPHER_SUITE.encrypt(address_in.street.encode()),
        house=CIPHER_SUITE.encrypt(str(address_in.house).encode()),
        apartment=encoded_apartment
    )

    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


def get_address(
        db: Session, address_id: int
    ) -> models.Address | None:
    """
    Возвращает адрес пациента
    """
    return db.query(models.Address) \
            .filter(models.Address.id == address_id) \
            .first()


def update_address(
        db: Session, address_id: int, address_optional: AddressOptional
    ) -> models.Address | None:
    """
    Обновляет информацию об адресе
    """
    encoded_address_data = {key: CIPHER_SUITE.encrypt(str(value).encode()) for key, value in address_optional.model_dump(exclude_unset=True).items() if value}

    result = db.query(models.Address) \
        .filter(models.Address.id == address_id) \
        .update(encoded_address_data)
    db.commit()

    if result == 1:
        return get_address(db, address_id)
    return None


def delete_address(
        db: Session, address_id: int
    ) -> models.Address | None:
    """
    Удаляет информацию об адресе
    """
    deleted_address = get_address(db, address_id)

    result = db.query(models.Address) \
        .filter(models.Address.id == address_id) \
        .delete()
    db.commit()

    if result == 1:
        return deleted_address
    return None
