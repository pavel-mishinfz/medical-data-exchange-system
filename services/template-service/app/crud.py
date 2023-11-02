import os
import uuid
from typing import List

from sqlalchemy.orm import Session
from .database import models


def create_template(
        db: Session, name: str, path_to_storage: str
    ) -> models.Template:
    """
    Создает новый шаблон в БД
    """
    db_template = models.Template(
        name=name,
        path=os.path.join(path_to_storage, str(uuid.uuid4()) + '.html')
    )

    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


def get_templates(db: Session) -> List[models.Template]:
    """
    Возвращает все шаблоны
    """
    return db.query(models.Template).all()


def get_template(
        db: Session, template_id: int
    ) -> models.Template | None:
    """
    Возвращает конкретный шаблон
    """
    return db.query(models.Template) \
            .filter(models.Template.id == template_id) \
            .first()


def update_template(
        db: Session, template_id: int, name: str
    ) -> models.Template | None:
    """
    Обновляет информацию о шаблоне
    """
    result = db.query(models.Template) \
        .filter(models.Template.id == template_id) \
        .update({models.Template.name: name})
    db.commit()

    if result == 1:
        return get_template(db, template_id)
    return None


def delete_template(
        db: Session, template_id: int
    ) -> models.Template | None:
    """
    Удаляет информацию о шаблоне
    """
    deleted_template = get_template(db, template_id)

    result = db.query(models.Template) \
        .filter(models.Template.id == template_id) \
        .delete()
    db.commit()

    if result == 1:
        return deleted_template
    return None
