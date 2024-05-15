import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .database import models


async def get_user(
        user_id: uuid.UUID, session: AsyncSession
    ) -> models.User:
    """
    Возвращает информацию о пользователе
    """

    result = await session.execute(select(models.User) \
                                   .filter(models.User.id == user_id) \
                                   .limit(1)
                                   )
    return result.scalars().one_or_none()


async def get_doctors_of_specialization(
        specialization_id: int,
        session: AsyncSession
    ) -> list[models.User]:
    """
    Возвращает список врачей конкретной специализации
    """

    result = await session.execute(select(models.User) \
                                   .filter(models.User.specialization_id == specialization_id))
    return result.scalars().all()


async def get_users_list(
        session: AsyncSession
    ) -> list[models.User]:
    """
    Возвращает список пользователей
    """

    result = await session.execute(select(models.User))
    return result.scalars().all()


async def update_img(
        path_to_file: str | None, user_id: uuid.UUID, session: AsyncSession
    ) -> models.User | None:
    """
    Обновляет фотографию пользователя
    """

    fields_for_update = {"img": path_to_file}
    result = await session.execute(update(models.User) \
                                   .where(models.User.id == user_id) \
                                   .values(fields_for_update)
                                   )
    await session.commit()
    if result:
        return await get_user(user_id, session)
    return None
