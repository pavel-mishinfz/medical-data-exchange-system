from datetime import datetime, timezone

from sqlalchemy.orm import Session
from .database import models
from .schemas import DocumentIn, DocumentOptional


def create_document(
        db: Session, document_in: DocumentIn, path_to_file: str
) -> models.Document:
    """
    Создает новый документ в БД
    """

    db_document = models.Document(
        name=document_in.name,
        description=document_in.description,
        id_page=document_in.id_page,
        path_to_file=path_to_file,
        create_date=datetime.now(timezone.utc)
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_document(
        db: Session, document_id: int
) -> models.Document | None:
    """
    Возвращает конкретный документ
    """
    return db.query(models.Document) \
        .filter(models.Document.id == document_id) \
        .first()


def update_document(
        db: Session, document_id: int, document_optional: DocumentOptional, path_to_file: str
) -> models.Document | None:
    """
    Обновляет информацию о документе
    """
    result = db.query(models.Document) \
        .filter(models.Document.id == document_id) \
        .update(document_optional.model_dump(exclude_unset=True) | {"path_to_file": path_to_file})
    db.commit()

    if result == 1:
        return get_document(db, document_id)
    return None


def delete_document(
        db: Session, document_id: int
) -> models.Document | None:
    """
    Удаляет информацию о документе
    """
    deleted_document = get_document(db, document_id)

    result = db.query(models.Document) \
        .filter(models.Document.id == document_id) \
        .delete()
    db.commit()

    if result == 1:
        return deleted_document
    return None
