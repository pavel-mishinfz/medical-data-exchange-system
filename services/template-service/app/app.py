import os
import pathlib

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from .schemas import Template, TemplateIn
from .database import DB_INITIALIZER
from . import crud, config


description = """
Содержит _название_ и _структуру_ шаблона.

Предназначен для: 

* **создания** 
* **получения**
* **обновления**
* **удаления**

шаблонов страниц электронной медицинской карты.

Структура шаблона состоит из следующих компонентов:

* **Заголовок поля** 
* **Значение**
* **Набор полей** (заголовок, тип, имя, значение по умолчанию)

"""

tags_metadata = [
    {
        "name": "templates",
        "description": "Операции с шаблонами",
    }
]

cfg: config.Config = config.load_config()
SessionLocal = DB_INITIALIZER.init_database(str(cfg.postgres_dsn))

app = FastAPI(title='Template Service',
              description=description,
              openapi_tags=tags_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_SERVICE_DIR = pathlib.Path(__file__).parent.parent.resolve()
app.mount("/storage", StaticFiles(directory=os.path.join(ROOT_SERVICE_DIR, "storage")), name="storage")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/templates', response_model=Template, summary='Добавляет шаблон в базу', tags=["templates"])
def add_template(
        template_in: TemplateIn,
        db: Session = Depends(get_db)
):
    return crud.create_template(db, template_in)


@app.get('/templates/{template_id}', response_model=Template, summary='Возвращает шаблон', tags=["templates"])
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = crud.get_template(db, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    return template


@app.get('/templates',
         response_model=list[Template],
         summary='Возвращает список всех шаблонов',
         tags=["templates"])
def get_templates(db: Session = Depends(get_db)):
    return crud.get_templates(db)


@app.put('/templates/{template_id}', response_model=Template, summary='Обновляет шаблон', tags=["templates"])
def update_template(
        template_id: int,
        template_in: TemplateIn,
        db: Session = Depends(get_db)
    ):
    template = crud.update_template(db, template_id, template_in)
    if template is None:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    return template


@app.delete(
    '/templates/{template_id}',
    response_model=Template,
    summary='Удаляет шаблон из базы',
    tags=["templates"]
    )
def delete_template(template_id: int, db: Session = Depends(get_db)):
    deleted_template = crud.delete_template(db, template_id)
    if deleted_template is None:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    return deleted_template
