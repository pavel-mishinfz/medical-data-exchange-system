from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from .database import models
from .schemas import (FamilyStatus,
                      Education,
                      Busyness)


def get_family_status(
        db: Session, family_status_id: int
    ) -> models.FamilyStatus | None:
    """
    Возвращает информацию о семейном положении
    """

    return db.query(models.FamilyStatus) \
        .filter(models.FamilyStatus.id == family_status_id) \
        .first()


def upsert_family_status(
        db: Session, family_status: FamilyStatus
    ) -> models.FamilyStatus | None:
    """
    Обновляет или добавляет статус семейного положения в базу
    """

    stm = insert(models.FamilyStatus).values(family_status.model_dump())
    stm = stm.on_conflict_do_update(
        constraint='family_status_pkey',
        set_={"name": family_status.name}
    )
    result = db.execute(stm)

    db.commit()
    if result:
        return get_family_status(db, family_status.id)
    return None


def get_education(
        db: Session, education_id: int
    ) -> models.Education | None:
    """
    Возвращает информацию об образовании
    """

    return db.query(models.Education) \
        .filter(models.Education.id == education_id) \
        .first()


def upsert_education(
        db: Session, education: Education
    ) -> models.Education | None:
    """
    Обновляет или добавляет тип образования в базу
    """

    stm = insert(models.Education).values(education.model_dump())
    stm = stm.on_conflict_do_update(
        constraint='education_pkey',
        set_={"name": education.name}
    )
    result = db.execute(stm)

    db.commit()
    if result:
        return get_education(db, education.id)
    return None


def get_busyness(
        db: Session, busyness_id: int
    ) -> models.Busyness | None:
    """
    Возвращает информацию о занятости
    """

    return db.query(models.Busyness) \
        .filter(models.Busyness.id == busyness_id) \
        .first()


def upsert_busyness(
        db: Session, busyness: Busyness
    ) -> models.Busyness | None:
    """
    Обновляет или добавляет тип занятости в базу
    """

    stm = insert(models.Busyness).values(busyness.model_dump())
    stm = stm.on_conflict_do_update(
        constraint='busyness_pkey',
        set_={"name": busyness.name}
    )
    result = db.execute(stm)

    db.commit()
    if result:
        return get_education(db, busyness.id)
    return None
