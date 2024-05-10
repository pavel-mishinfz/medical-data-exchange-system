import math
import random
from datetime import datetime, timezone
import uuid
from typing import List

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .database import models


async def upsert_confirm_code(session: AsyncSession,
                              user_id: uuid.UUID) -> models.ConfirmCode | None:
    """
    Обновляет или добавляет код подтверждения в базу
    """
    confirm_code = ""
    for _ in range(6):
        confirm_code += str(math.floor(random.random() * 10))
    data = {
        "user_id": user_id,
        "code": confirm_code,
        "create_date": datetime.now(timezone.utc)
    }
    stm = insert(models.ConfirmCode).values(data)
    stm = stm.on_conflict_do_update(
        constraint='confirm_code_pkey',
        set_={"code": data["code"], "create_date": data["create_date"]}
    )
    result = await session.execute(stm)

    await session.commit()
    if result:
        return await get_confirm_code(session, user_id)
    return None


async def get_confirm_code(session: AsyncSession,
                           user_id: uuid.UUID) -> models.ConfirmCode:
    """
    Возвращает информацию о коде подтверждения
    """
    result = await session.execute(select(models.ConfirmCode).filter(models.ConfirmCode.user_id == user_id).limit(1))
    return result.scalars().one_or_none()


async def get_old_confirm_codes(session: AsyncSession,
                                expired_time: datetime) -> List[models.ConfirmCode]:
    """
    Возвращает информацию об истекших кодах подтверждения
    """
    result = await session.execute(select(models.ConfirmCode)
                                   .filter(models.ConfirmCode.create_date < expired_time))
    return result.scalars().all()


async def delete_confirm_code(session: AsyncSession,
                              user_id: uuid.UUID) -> bool:
    """
    Удаляет информацию о коде подтверждения
    """
    has_confirm_code = await get_confirm_code(session, user_id)
    await session.execute(delete(models.ConfirmCode).filter(models.ConfirmCode.user_id == user_id))
    await session.commit()
    return bool(has_confirm_code)