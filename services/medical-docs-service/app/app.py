import os
import pathlib
import uuid
from typing import Optional, Union
from fastapi import FastAPI, UploadFile, Depends, HTTPException, Body, File
from sqlalchemy.orm import Session
from .schemas import Document, DocumentIn
from .database import DB_INITIALIZER
from . import crud, config

from pydicom import dcmread
from pydicom.errors import InvalidDicomError


description = """"""

tags_metadata = [
    {
        "name": "documents",
        "description": "Операции с меддокументами",
    }
]

cfg: config.Config = config.load_config()
SessionLocal = DB_INITIALIZER.init_database(str(cfg.postgres_dsn))
EXTENSION_PDF = '.pdf'
EXTENSION_DCM = '.dcm'

app = FastAPI(title='Medical Docs Service',
              description=description,
              openapi_tags=tags_metadata)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post(
    '/documents/template/{template_id}/page/{page_id}',
    response_model=Document,
    summary='Добавляет документ в базу в формате pdf или dicom',
    tags=["documents"]
)
def add_document(
        page_id: int, 
        template_id: int, 
        document_in: DocumentIn = Body(...), 
        file: UploadFile = File(...), 
        db: Session = Depends(get_db)
    ):
    if file.content_type == 'application/pdf':
        path_to_file = create_path_to_file(cfg.path_to_storage, EXTENSION_PDF)
        new_document = crud.create_document(
            db, document_in, page_id, template_id, path_to_file
        )
        create_pdf_file(file, new_document.path_to_file)
    else:
        path_to_file = create_path_to_file(cfg.path_to_storage, EXTENSION_DCM)
        new_document = crud.create_document(
            db, document_in, page_id, template_id, path_to_file
        )
        create_dcm_file(file, new_document.path_to_file)
    return new_document


@app.get('/documents/{document_id}', response_model=Document, summary='Возвращает документ', tags=["documents"])
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = crud.get_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Документ не найден")
    return document


@app.put('/documents/{document_id}', response_model=Document, summary='Обновляет документ', tags=["documents"])
def update_document(
        document_id: int,
        document_in: DocumentIn,
        file: UploadFile = File(None),
        db: Session = Depends(get_db)
    ):
    document = crud.get_document(db, document_id)
    if document is not None:
        path_to_file = document.path_to_file
        if file:
            delete_file_from_storage(path_to_file)
            if file.content_type == 'application/pdf':
                path_to_file = create_path_to_file(cfg.path_to_storage, EXTENSION_PDF)
                create_pdf_file(file, path_to_file)
            else:
                path_to_file = create_path_to_file(cfg.path_to_storage, EXTENSION_DCM)
                create_dcm_file(file, path_to_file)
        return crud.update_document(db, document_id, document_in, path_to_file)
    raise HTTPException(status_code=404, detail="Документ не найден")


@app.delete(
    '/documents/{document_id}',
    response_model=Document,
    summary='Удаляет документ из базы',
    tags=["documents"]
    )
def delete_documents(document_id: int, db: Session = Depends(get_db)):
    deleted_document = crud.delete_document(db, document_id)
    if deleted_document is None:
        raise HTTPException(status_code=404, detail="Документ не найден")
    delete_file_from_storage(deleted_document.path_to_file)
    return deleted_document


def create_dcm_file(file: UploadFile, path_to_file: str):
    try:
        dcm_file = dcmread(file.file)
        dcm_file.save_as(path_to_file)
    except InvalidDicomError:
        raise HTTPException(status_code=400, detail="Недопустимый тип файла")


def create_pdf_file(file: UploadFile, path_to_file: str):
    with open(path_to_file, 'wb') as out_file:
        out_file.write(file.file.read())


def create_path_to_file(path_to_storage: str, extension: str):
    return os.path.join(path_to_storage, str(uuid.uuid4()) + extension)


def delete_file_from_storage(path_to_file: str):
    os.remove(path_to_file)
