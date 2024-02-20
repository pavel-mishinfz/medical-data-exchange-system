import uuid

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import PageDiary, PageDiaryIn, PageDiaryOptional, PageDiaryShortOut
from .database import DB_INITIALIZER, get_async_session
from . import crud, config

description = """

"Дневник здоровья" содержит следующие поля: 

* _пульс_
* _температура тела_ 
* _артериальное давление_ (верхнее и нижнее) 
* _уровень кислорода в крови_
* _уровень сахара в крови_
* _комментарий пациента_

Сервис предназначен для: 

* **создания** 
* **получения**
* **обновления**
* **удаления**

информации о "Дневнике здоровья" пациента.
 
"""

tags_metadata = [
    {
        "name": "diaries",
        "description": "Операции с дневниками здоровья",
    }
]

cfg: config.Config = config.load_config()

app = FastAPI(title='Health Diary Service',
              description=description,
              openapi_tags=tags_metadata)


@app.post(
    '/diaries/user/{user_id}',
    response_model=PageDiary,
    summary='Добавляет страницу дневника здоровья в базу',
    tags=["diaries"]
)
async def add_diary(user_id: uuid.UUID, page_diary_in: PageDiaryIn, db: AsyncSession = Depends(get_async_session)):
    return await crud.create_page_diary(db, user_id, page_diary_in)


@app.get(
    '/diaries/{page_diary_id}',
    response_model=PageDiary,
    summary='Возвращает страницу дневника',
    tags=["diaries"]
)
async def get_diary(page_diary_id: int, db: AsyncSession = Depends(get_async_session)):
    page_diary = await crud.get_page_diary(db, page_diary_id)
    if page_diary is None:
        raise HTTPException(status_code=404, detail="Страница не найдена")
    return page_diary


@app.get(
    '/diaries/user/{user_id}',
    response_model=list[PageDiaryShortOut],
    summary='Возвращает все идентификаторы страниц дневника пользователя',
    tags=["diaries"]
)
async def get_diary(user_id: uuid.UUID, db: AsyncSession = Depends(get_async_session)):
    return await crud.get_page_diary_id_list(db, user_id)


@app.patch(
    '/diaries/{page_diary_id}',
    response_model=PageDiary,
    summary='Обновляет страницу дневника',
    tags=["diaries"]
)
async def update_page(
        page_diary_id: int,
        page_diary_optional: PageDiaryOptional,
        db: AsyncSession = Depends(get_async_session)
):
    diary = await crud.update_page_diary(db, page_diary_id, page_diary_optional)
    if diary is None:
        raise HTTPException(status_code=404, detail="Страница не найдена")
    return diary


@app.delete(
    '/diaries/{page_diary_id}',
    summary='Удаляет страницу дневника из базы',
    response_model=PageDiary,
    tags=["diaries"]
)
async def delete_diary(page_diary_id: int, db: AsyncSession = Depends(get_async_session)):
    deleted_page_diary = await crud.delete_page_diary(db, page_diary_id)
    if deleted_page_diary is None:
        raise HTTPException(status_code=404, detail="Страница не найдена")
    return deleted_page_diary


@app.on_event("startup")
async def on_startup():
    await DB_INITIALIZER.init_database(
        cfg.postgres_dsn_async.unicode_string()
    )
