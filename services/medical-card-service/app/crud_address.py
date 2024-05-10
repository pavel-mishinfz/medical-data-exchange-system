from sqlalchemy.orm import Session

from .database import models
from .schemas import AddressIn, AddressOptional


def create_address(db: Session, address_in: AddressIn) -> models.Address:
    """
    Создает новую запись адреса в БД
    """
    db_address = models.Address(
        subject=address_in.subject,
        district=address_in.district,
        locality=address_in.locality,
        street=address_in.street,
        house=address_in.house,
        apartment=address_in.apartment
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
    result = db.query(models.Address) \
        .filter(models.Address.id == address_id) \
        .update(address_optional.model_dump(exclude_unset=True))
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
