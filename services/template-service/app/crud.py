import os
import uuid

from sqlalchemy.orm import Session
from .database import models
from .schemas import TemplateIn


def create_template(
        db: Session, template_in: TemplateIn, path_to_file: str
    ) -> models.Template:
    """
    Создает новый шаблон в БД
    """
    db_template = models.Template(
        name=template_in.name,
        path_to_file=path_to_file
    )

    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


def get_templates(db: Session) -> list[models.Template]:
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
        db: Session, template_id: int, template_in: TemplateIn
    ) -> models.Template | None:
    """
    Обновляет информацию о шаблоне
    """
    result = db.query(models.Template) \
        .filter(models.Template.id == template_id) \
        .update({models.Template.name: template_in.name})
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
