import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .database import models
from .schemas import user


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


async def update_user(
        user_id: uuid.UUID, user: user.UserUpdate, session: AsyncSession
    ) -> models.User | None:
    """
    Обновляет основную информацию о пользователе
    """
    excluded_fields = {
        'email': user.email,
        'password': user.password,
        'group_id': user.group_id,
        'is_active': user.is_active,
        'is_verified': user.is_verified,
        'is_superuser': user.is_superuser
    }
    user_in = user.model_dump(exclude=excluded_fields, exclude_unset=True)
    result = await session.execute(update(models.User) \
                                   .where(models.User.id == user_id) \
                                   .values(user_in)
                                   )
    await session.commit()
    if result:
        return await get_user(user_id, session)
    return None


async def update_user_email(
        user_id: uuid.UUID, email: str, session: AsyncSession
    ) -> models.User | None:
    """
    Обновляет email пользователя
    """
    result = await session.execute(update(models.User) \
                                   .where(models.User.id == user_id) \
                                   .values({"email": email, "is_verified": False})
                                   )
    await session.commit()
    if result:
        return await get_user(user_id, session)
    return None


async def get_doctor(
        doctor_id: uuid.UUID, session: AsyncSession
    ) -> models.User:
    """
    Возвращает информацию о враче
    """

    result = await session.execute(select(models.User) \
                                   .filter(models.User.group_id == 2, models.User.id == doctor_id) \
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
