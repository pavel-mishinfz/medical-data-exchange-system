import datetime
import uuid

from sqlalchemy import delete, select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from .database import models
from .schemas import RecordIn, RecordOptional, ScheduleIn, ScheduleOptional


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
        db: AsyncSession,
        user_id: uuid.UUID = None,
        doctor_id: uuid.UUID = None
    ) -> list[models.Record] | None:
    """
    Возвращает список записей на приемы для пациента/врача
    """
    result = await db.execute(select(models.Record) \
                              .filter(
                                  or_ (
                                      models.Record.id_user == user_id,
                                      models.Record.id_doctor == doctor_id
                                      ))
                              .filter(models.Record.date >= datetime.datetime.today().date())  
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


async def create_schedule(
        db: AsyncSession, schedule_in: ScheduleIn
    ) -> models.Schedule:
    """
    Создает новый график работы врача в БД
    """
    db_schedule = models.Schedule(
        id_doctor=schedule_in.id_doctor,
        schedule=schedule_in.schedule,
        time_per_patient=schedule_in.time_per_patient
    )

    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)
    return db_schedule


async def get_schedule(
        db: AsyncSession, schedule_id: int | None, doctor_id: uuid.UUID | None
    ) -> models.Schedule | None:
    """
    Возвращает график работы врача
    """
    result = await db.execute(select(models.Schedule) \
                              .filter(
                                or_(
                                models.Schedule.id == schedule_id,
                                models.Schedule.id_doctor == doctor_id)) \
                              .limit(1)
                              )
    return result.scalars().one_or_none()


async def update_schedule(
        db: AsyncSession, schedule_id: int, schedule_optional: ScheduleOptional
    ) -> models.Schedule | None:
    """
    Обновляет информацию о графике работы врача
    """
    result = await db.execute(update(models.Schedule) \
                              .where(models.Schedule.id == schedule_id) \
                              .values(schedule_optional.model_dump(exclude_unset=True))
                              )
    await db.commit()

    if result:
        return await get_schedule(db, schedule_id)
    return None


async def delete_schedule(
        db: AsyncSession, schedule_id: int
    ) -> models.Schedule | None:
    """
    Удаляет информацию о графике работы врача
    """
    deleted_schedule = await get_schedule(db, schedule_id)
    await db.execute(delete(models.Schedule) \
                     .filter(models.Schedule.id == schedule_id)
                     )

    await db.commit()

    return deleted_schedule
