from sqlalchemy.orm import Session

from .database import models
from .schemas import DisabilityIn, DisabilityOptional


def create_disability(db: Session, disability_in: DisabilityIn) -> models.Disability:
    """
    Создает новую запись инвалидности в БД
    """
    db_disability = models.Disability(
        name=disability_in.name,
        group=disability_in.group,
        create_date=disability_in.create_date
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
    result = db.query(models.Disability) \
        .filter(models.Disability.id == disability_id) \
        .update(disability_optional.model_dump(exclude_unset=True))
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
