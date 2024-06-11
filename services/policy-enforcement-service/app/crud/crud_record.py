import uuid
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..database import models


def get_available_records(db: Session, user_id: uuid.UUID):
    """
    Возвращает список идентификаторов записей на прием
    """
    records = (db.query(models.Records.id)
            .filter(
                or_(
                    models.Records.id_doctor == user_id,
                    models.Records.id_user == user_id
                )
            )
            .all())
    return [record[0] for record in records]