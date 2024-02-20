import json
import uuid

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import (Card,
                      CardIn,
                      CardOptional,
                      Page,
                      PageIn,
                      PageShortOut,
                      FamilyStatus,
                      Education,
                      Busyness)
from .database import DB_INITIALIZER
from . import crud, config, crud_config


description = """
Медкарта содержит _идентификатор пользователя_ и _ФИО пациента_.

Страница медкарты содержит _идентификатор карты_, 
_идентификатор пользователя_ и _данные_, полученные с шаблона.

Сервис предназначен для: 

* **создания** 
* **получения**
* **обновления**
* **удаления**

медицинских карт и их страниц.
 
"""

tags_metadata = [
    {
        "name": "cards",
        "description": "Операции с медкартами",
    },
    {
        "name": "pages",
        "description": "Операции со страницами медкарт",
    }
]

cfg: config.Config = config.load_config()
SessionLocal = DB_INITIALIZER.init_database(str(cfg.postgres_dsn))

app = FastAPI(title='Medical Card Service',
              description=description,
              openapi_tags=tags_metadata)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/cards/user/{user_id}', response_model=Card, summary='Добавляет медкарту в базу', tags=["cards"])
def add_card(user_id: uuid.UUID, card_in: CardIn, db: Session = Depends(get_db)):
    return crud.create_card(db, user_id, card_in)


@app.get('/cards/{card_id}', response_model=tuple[Card, list[PageShortOut]], summary='Возвращает медкарту', tags=["cards"])
def get_card(card_id: int, db: Session = Depends(get_db)):
    card, pages = crud.get_card_with_pages(db, card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Медкарта не найдена")
    return card, pages


@app.patch('/cards/{card_id}', response_model=Card, summary='Обновляет медкарту', tags=["cards"])
def update_card(
        card_id: int,
        card_optional: CardOptional,
        db: Session = Depends(get_db)
    ):
    card = crud.update_card(db, card_id, card_optional)
    if card is not None:
        return card
    raise HTTPException(status_code=404, detail="Медкарта не найдена")


@app.delete(
    '/cards/{card_id}',
    summary='Удаляет медкарту из базы',
    response_model=Card,
    tags=["cards"]
    )
def delete_card(card_id: int, db: Session = Depends(get_db)):
    deleted_card = crud.delete_card(db, card_id)
    if deleted_card is None:
        raise HTTPException(status_code=404, detail="Медкарта не найден")
    return deleted_card


@app.post(
    '/pages/card/{card_id}/template/{template_id}',
    response_model=Page,
    summary='Добавляет страницу в базу',
    tags=["pages"]
    )
def add_page(card_id: int, template_id: int, page_in: PageIn, db: Session = Depends(get_db)):
    card = crud.get_card(db, card_id)
    if card:
        return crud.create_page(db, card_id, template_id, page_in)
    raise HTTPException(status_code=404, detail="Медкарта не найден")


@app.get('/pages/{page_id}', response_model=Page, summary='Возвращает страницу', tags=["pages"])
def get_page(page_id: int, db: Session = Depends(get_db)):
    page = crud.get_page(db, page_id)
    if page is None:
        raise HTTPException(status_code=404, detail="Страница не найдена")
    return page


@app.patch('/pages/{page_id}', response_model=Page, summary='Обновляет страницу', tags=["pages"])
def update_page(
        page_id: int,
        page_in: PageIn,
        db: Session = Depends(get_db)
    ):
    page = crud.update_page(db, page_id, page_in)
    if page is not None:
        return page
    raise HTTPException(status_code=404, detail="Страница не найдена")


@app.delete(
    '/pages/{page_id}',
    response_model=Page,
    summary='Удаляет страницу из базы',
    tags=["pages"]
    )
def delete_page(page_id: int, db: Session = Depends(get_db)):
    deleted_page = crud.delete_page(db, page_id)
    if deleted_page is None:
        raise HTTPException(status_code=404, detail="Страница не найден")
    return deleted_page


@app.on_event("startup")
def on_startup():

    data = []
    with open(cfg.default_data_config_path) as f:
        data = json.load(f)

    for item in data:
        for key, value in item.items():
            if key == 'family-status':
                make_family_status_table(value)
            elif key == 'education':
                make_education_table(value)
            elif key == 'busyness':
                make_busyness_table(value)


def make_family_status_table(data):
    for session in get_db():
        for item in data:
            crud_config.upsert_family_status(
                session, FamilyStatus(**item)
            )


def make_education_table(data):
    for session in get_db():
        for item in data:
            crud_config.upsert_education(
                session, Education(**item)
            )


def make_busyness_table(data):
    for session in get_db():
        for item in data:
            crud_config.upsert_busyness(
                session, Busyness(**item)
            )
