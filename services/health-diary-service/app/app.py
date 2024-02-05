from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import Diary, DiaryIn, PageDiary, PageDiaryIn
from .database import DB_INITIALIZER
from . import crud, config

description = """"""

tags_metadata = [
    {
        "name": "diaries",
        "description": "Операции с дневниками здоровья",
    },
    {
        "name": "pages-diary",
        "description": "Операции со страницами дневника",
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
    '/diaries/user/{user_id}', response_model=Diary, summary='Добавляет дневник здоровья в базу', tags=["diaries"]
)
def add_diary(user_id: int, db: Session = Depends(get_db)):
    return crud.create_diary(db, user_id)


@app.get('/diaries/{diary_id}', summary='Возвращает дневник', tags=["diaries"])
def get_diary(diary_id: int, db: Session = Depends(get_db)):
    diary = crud.get_diary(db, diary_id)
    if diary is None:
        raise HTTPException(status_code=404, detail="Дневник не найден")
    return diary


@app.delete(
    '/diaries/{diary_id}',
    summary='Удаляет дневник из базы',
    response_model=Diary,
    tags=["diaries"]
)
def delete_diary(diary_id: int, db: Session = Depends(get_db)):
    deleted_diary = crud.delete_diary(db, diary_id)
    if deleted_diary is None:
        raise HTTPException(status_code=404, detail="Дневник не найден")
    return deleted_diary


@app.post(
    '/pages/{diary_id}',
    response_model=PageDiary,
    summary='Добавляет страницу в базу',
    tags=["pages-diary"]
)
def add_page(diary_id: int, page_in: PageDiaryIn, db: Session = Depends(get_db)):
    return crud.create_page(db, diary_id, page_in)


@app.get('/pages/{page_id}', response_model=PageDiary, summary='Возвращает страницу', tags=["pages-diary"])
def get_page(page_id: int, db: Session = Depends(get_db)):
    page = crud.get_page(db, page_id)
    if page is None:
        raise HTTPException(status_code=404, detail="Страница не найдена")
    return page


@app.put('/pages/{page_id}', response_model=PageDiary, summary='Обновляет страницу', tags=["pages-diary"])
def update_page(
        page_id: int,
        page_in: PageDiaryIn,
        db: Session = Depends(get_db)
):
    page = crud.update_page(db, page_id, page_in)
    if page is not None:
        return page
    raise HTTPException(status_code=404, detail="Страница не найдена")


@app.delete(
    '/pages/{page_id}',
    response_model=PageDiary,
    summary='Удаляет страницу из базы',
    tags=["pages-diary"]
)
def delete_page(page_id: int, db: Session = Depends(get_db)):
    deleted_page = crud.delete_page(db, page_id)
    if deleted_page is None:
        raise HTTPException(status_code=404, detail="Страница не найден")
    return deleted_page
