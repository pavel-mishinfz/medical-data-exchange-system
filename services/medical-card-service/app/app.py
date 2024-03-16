import json
import os
import pathlib
import uuid

from fastapi import FastAPI, Depends, HTTPException, Body, UploadFile, File
from pydicom import dcmread
from sqlalchemy.orm import Session
from .schemas import (Card,
                      CardIn,
                      CardOptional,
                      Page,
                      PageIn,
                      PageShortOut,
                      FamilyStatus,
                      Education,
                      Busyness,
                      DocumentIn,
                      DocumentOptional,
                      Document)
from .database import DB_INITIALIZER
from . import crud, config, crud_config, crud_document


description = """
Медкарта содержит _идентификатор пользователя_ и главную информацию о нем.

Страница медкарты содержит _идентификатор карты_, 
_идентификатор пользователя_, _данные_, полученные с шаблона, а также _медицинские документы_ (если имеются).

Сервис предназначен для: 

* **создания** 
* **получения**
* **обновления**
* **удаления**

медицинских карт и их страниц, а также медицинских документов.
 
"""

tags_metadata = [
    {
        "name": "cards",
        "description": "Операции с медкартами",
    },
    {
        "name": "pages",
        "description": "Операции со страницами медкарт",
    },
    {
        "name": "documents",
        "description": "Операции с меддокументами",
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


@app.put('/pages/{page_id}', response_model=Page, summary='Обновляет страницу', tags=["pages"])
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
    deleted_page, documents = crud.delete_page(db, page_id)
    if deleted_page is None:
        raise HTTPException(status_code=404, detail="Страница не найден")
    remove_documents_of_page_from_storage(documents)
    return deleted_page


@app.post(
    '/documents',
    response_model=list[Document],
    summary='Добавляет документы в базу в формате pdf/dicom',
    tags=["documents"]
)
def add_documents(
        document_in: DocumentIn = Body(...),
        files: list[UploadFile] = File(...),
        db: Session = Depends(get_db)
    ):
    page = crud.get_page(db, document_in.id_page)
    if page is None:
        raise HTTPException(status_code=404, detail="Страница не найдена")
    for file in files:
        path_to_file = create_path_to_file(cfg.path_to_storage, file.filename)
        if file.content_type == 'application/pdf':
            create_pdf_file(file, path_to_file)
        elif file.content_type == 'application/dicom':
            create_dcm_file(file, path_to_file)
        crud_document.create_document(db, document_in, path_to_file)
    return page.documents


@app.get('/documents/{document_id}', response_model=Document, summary='Возвращает документ', tags=["documents"])
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = crud_document.get_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Документ не найден")
    return document


@app.patch('/documents/{document_id}', response_model=Document, summary='Обновляет документ', tags=["documents"])
def update_document(
        document_id: int,
        document_optional: DocumentOptional,
        file: UploadFile = File(None),
        db: Session = Depends(get_db)
    ):
    document = crud_document.get_document(db, document_id)
    if document is not None:
        path_to_file = document.path_to_file
        extension_existing_file = pathlib.Path(path_to_file).suffix
        if file:
            if file.content_type == 'application/pdf':
                path_to_file = update_pdf_file(file, extension_existing_file, cfg.path_to_storage, path_to_file)
            elif file.content_type == 'application/dicom':
                path_to_file = update_dcm_file(file, extension_existing_file, cfg.path_to_storage, path_to_file)
            else:
                raise HTTPException(status_code=400, detail="Недопустимый тип файла")
        return crud_document.update_document(db, document_id, document_optional, path_to_file)
    raise HTTPException(status_code=404, detail="Документ не найден")


@app.delete(
    '/documents/{document_id}',
    response_model=Document,
    summary='Удаляет документ из базы',
    tags=["documents"]
    )
def delete_documents(document_id: int, db: Session = Depends(get_db)):
    deleted_document = crud_document.delete_document(db, document_id)
    if deleted_document is None:
        raise HTTPException(status_code=404, detail="Документ не найден")
    delete_file_from_storage(deleted_document.path_to_file)
    return deleted_document


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


def create_dcm_file(file: UploadFile, path_to_file: str):
    try:
        dcm_file = dcmread(file.file)
        dcm_file.save_as(path_to_file)
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка при работе с файлом")


def update_dcm_file(file: UploadFile, extension_existing_file: str, path_to_storage: str, path_to_file: str):
    extension = pathlib.Path(file.filename).suffix
    if extension_existing_file != extension:
        delete_file_from_storage(path_to_file)
        path_to_file = create_path_to_file(path_to_storage, extension)
    create_dcm_file(file, path_to_file)
    return path_to_file


def create_pdf_file(file: UploadFile, path_to_file: str):
    try:
        with open(path_to_file, 'wb') as out_file:
            out_file.write(file.file.read())
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка при работе с файлом")


def update_pdf_file(file: UploadFile, extension_existing_file: str, path_to_storage: str, path_to_file: str):
    extension = pathlib.Path(file.filename).suffix
    if extension_existing_file != extension:
        delete_file_from_storage(path_to_file)
        path_to_file = create_path_to_file(path_to_storage, extension)
    create_pdf_file(file, path_to_file)
    return path_to_file


def create_path_to_file(path_to_storage: str, file_name: str):
    extension = pathlib.Path(file_name).suffix
    return os.path.join(path_to_storage, str(uuid.uuid4()) + extension)


def remove_documents_of_page_from_storage(documents):
    for document in documents:
        delete_file_from_storage(document.path_to_file)


def delete_file_from_storage(path_to_file: str):
    os.remove(path_to_file)
