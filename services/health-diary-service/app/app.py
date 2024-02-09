import uuid

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import PageDiary, PageDiaryIn
from .database import DB_INITIALIZER
from . import crud, config

description = """"""

tags_metadata = [
    {
        "name": "diaries",
        "description": "Операции с дневниками здоровья",
    }
]

cfg: config.Config = config.load_config()
SessionLocal = DB_INITIALIZER.init_database(str(cfg.postgres_dsn))

app = FastAPI(title='Health Diary Service',
              description=description,
              openapi_tags=tags_metadata)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post(
    '/diaries/user/{user_id}',
    response_model=PageDiary,
    summary='Добавляет страницу дневника здоровья в базу',
    tags=["diaries"]
)
def add_diary(user_id: uuid.UUID, page_diary_in: PageDiaryIn, db: Session = Depends(get_db)):
    return crud.create_page_diary(db, user_id, page_diary_in)


@app.get(
    '/diaries/{page_diary_id}',
    response_model=PageDiary,
    summary='Возвращает страницу дневника',
    tags=["diaries"]
)
def get_diary(page_diary_id: int, db: Session = Depends(get_db)):
    page_diary = crud.get_page_diary(db, page_diary_id)
    if page_diary is None:
        raise HTTPException(status_code=404, detail="Страница не найдена")
    return page_diary


@app.get(
    '/diaries/user/{user_id}',
    response_model=list[PageDiary],
    summary='Возвращает все страницы дневника пользователя',
    tags=["diaries"]
)
def get_diary(user_id: uuid.UUID, db: Session = Depends(get_db)):
    return crud.get_page_diary_list(db, user_id)


@app.put(
    '/diaries/{page_diary_id}',
    response_model=PageDiary,
    summary='Обновляет страницу дневника',
    tags=["diaries"]
)
def update_page(
        page_diary_id: int,
        page_diary_in: PageDiaryIn,
        db: Session = Depends(get_db)
):
    diary = crud.update_page_diary(db, page_diary_id, page_diary_in)
    if diary is None:
        raise HTTPException(status_code=404, detail="Страница не найдена")
    return diary


@app.delete(
    '/diaries/{page_diary_id}',
    summary='Удаляет дневник из базы',
    response_model=PageDiary,
    tags=["diaries"]
)
def delete_diary(page_diary_id: int, db: Session = Depends(get_db)):
    deleted_page_diary = crud.delete_page_diary(db, page_diary_id)
    if deleted_page_diary is None:
        raise HTTPException(status_code=404, detail="Страница не найдена")
    return deleted_page_diary

