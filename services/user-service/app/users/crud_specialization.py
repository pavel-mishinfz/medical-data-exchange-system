import typing

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .database import models
from . import schemas


async def create_specialization(
        specialization: schemas.specialization.SpecializationIn, session: AsyncSession
    ) -> models.Specialization:
    """
    Создает новую специализацию в базе
    """

    db_specialization = models.Specialization(
        name=specialization.name
    )

    session.add(db_specialization)
    await session.commit()
    await session.refresh(db_specialization)
    return db_specialization


async def get_specialization_list(
        session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> typing.List[models.Specialization]:
    """
    Возвращает список специализаций
    """

    result = await session.execute(select(models.Specialization) \
                                   .offset(skip) \
                                   .limit(limit)
                                   )
    return result.scalars().all()


async def get_specialization(
        session: AsyncSession, specialization_id: int
    ) -> models.Specialization:
    """
    Возвращает информацию о специализации
    """

    result = await session.execute(select(models.Specialization) \
                                   .filter(models.Specialization.id == specialization_id) \
                                   .limit(1)
                                   )
    return result.scalars().one_or_none()


async def update_specialization(
        session: AsyncSession, specialization_id: int, specialization: schemas.specialization.SpecializationOptional
    ) -> models.Specialization | None:
    """
    Обновляет информацию о специализации
    """

    result = await session.execute(update(models.Specialization) \
                                   .where(models.Specialization.id == specialization_id) \
                                   .values(specialization.model_dump(exclude_unset=True))
                                   )
    await session.commit()
    if result:
        return await get_specialization(session, specialization_id)
    return None


async def delete_specialization(
        session: AsyncSession, specialization_id: int
    ) -> bool:
    """
    Удаляет информацию о специализации
    """

    has_specialization = await get_specialization(session, specialization_id)
    await session.execute(delete(models.Specialization) \
                          .filter(models.Specialization.id == specialization_id)
                          )
    await session.commit()
    return bool(has_specialization)
