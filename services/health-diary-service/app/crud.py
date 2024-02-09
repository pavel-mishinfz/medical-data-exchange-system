import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from .database import models
from .schemas import PageDiaryIn


async def create_page_diary(
        db: AsyncSession, user_id: uuid.UUID, page_diary_in: PageDiaryIn
    ) -> models.PageDiary:
    """
    Создает новую страницу дневника здоровья в БД
    """
    db_page_diary = models.PageDiary(
        id_user=user_id,
        pulse=page_diary_in.pulse,
        comment=page_diary_in.comment,
        create_date=datetime.now(timezone.utc)
    )

    db.add(db_page_diary)
    await db.commit()
    await db.refresh(db_page_diary)
    return db_page_diary


async def get_page_diary(
        db: AsyncSession, page_diary_id: int
    ) -> models.PageDiary | None:
    """
    Возвращает страницу дневника
    """
    result = await db.execute(select(models.PageDiary) \
                              .filter(models.PageDiary.id == page_diary_id) \
                              .limit(1)
                              )
    return result.scalars().one_or_none()


async def get_page_diary_list(
        db: AsyncSession, user_id: uuid.UUID
    ) -> list[models.PageDiary] | None:
    """
    Возвращает все страницы дневника пользователя
    """
    result = await db.execute(select(models.PageDiary) \
                              .filter(models.PageDiary.id_user == user_id)
                              )
    return result.scalars().all()


async def update_page_diary(
        db: AsyncSession, page_diary_id: int, page_diary_in: PageDiaryIn
    ) -> models.PageDiary | None:
    """
    Обновляет информацию о старнице
    """
    result = await db.execute(update(models.PageDiary) \
                              .where(models.PageDiary.id == page_diary_id) \
                              .values(page_diary_in.model_dump())
                              )
    await db.commit()

    if result:
        return await get_page_diary(db, page_diary_id)
    return None


async def delete_page_diary(
        db: AsyncSession, page_diary_id: int
    ) -> models.PageDiary | None:
    """
    Удаляет информацию о странице дневнике
    """
    deleted_page_diary = await get_page_diary(db, page_diary_id)
    await db.execute(delete(models.PageDiary) \
                     .filter(models.PageDiary.id == page_diary_id)
                     )

    await db.commit()

    return deleted_page_diary
