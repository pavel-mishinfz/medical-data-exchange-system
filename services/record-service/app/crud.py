import uuid

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from .database import models
from .schemas import RecordIn, RecordOptional


async def create_record(
        db: AsyncSession, record_in: RecordIn
    ) -> models.Record:
    """
    Создает новую запись пациента на прием в БД
    """
    db_record = models.Record(
        **record_in.model_dump()
    )

    db.add(db_record)
    await db.commit()
    await db.refresh(db_record)
    return db_record


async def get_record(
        db: AsyncSession, record_id: int
    ) -> models.Record | None:
    """
    Возвращает запись пациента на прием
    """
    result = await db.execute(select(models.Record) \
                              .filter(models.Record.id == record_id) \
                              .limit(1)
                              )
    return result.scalars().one_or_none()


async def get_record_list(
        db: AsyncSession, user_id: uuid.UUID
    ) -> list[models.Record] | None:
    """
    Возвращает все записи пациента на приемы
    """
    result = await db.execute(select(models.Record) \
                              .filter(models.Record.id_user == user_id)
                              )
    return result.scalars().all()


async def update_record(
        db: AsyncSession, record_id: int, record_optional: RecordOptional
    ) -> models.Record | None:
    """
    Обновляет информацию о записи пациента на прием
    """
    result = await db.execute(update(models.Record) \
                              .where(models.Record.id == record_id) \
                              .values(record_optional.model_dump(exclude_unset=True))
                              )
    await db.commit()

    if result:
        return await get_record(db, record_id)
    return None


async def delete_record(
        db: AsyncSession, record_id: int
    ) -> models.Record | None:
    """
    Удаляет информацию о записи пациента на прием
    """
    deleted_record = await get_record(db, record_id)
    await db.execute(delete(models.Record) \
                     .filter(models.Record.id == record_id)
                     )

    await db.commit()

    return deleted_record
