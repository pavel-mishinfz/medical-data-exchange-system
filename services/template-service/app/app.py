import os
import pathlib
import uuid

from fastapi import FastAPI, UploadFile, Depends, HTTPException, Body, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session

from .schemas import Template, TemplateIn, TemplateOut
from .database import DB_INITIALIZER
from . import crud, config


description = """
Содержит _название шаблона_ и _путь к файлу_.

Предназначен для: 

* **создания** 
* **получения**
* **обновления**
* **удаления**

шаблонов страниц медицинской карты или медицинских документов.

Также имеется возможность получить _все шаблоны_. 
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

ROOT_SERVICE_DIR = pathlib.Path(__file__).parent.parent.parent.resolve()
app.mount("/storage", StaticFiles(directory=os.path.join(ROOT_SERVICE_DIR, "storage")), name="storage")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/templates', response_model=TemplateOut, summary='Добавляет шаблон в базу', tags=["templates"])
def add_template(
        template_in: TemplateIn = Body(...),
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    if file.content_type == "text/html":
        path_to_file = create_path_to_file(cfg.path_to_storage, '.html')
        new_template = crud.create_template(db, template_in, path_to_file)
        create_html_file(file, new_template.path_to_file)
        return new_template
    raise HTTPException(status_code=400, detail="Недопустимый тип файла")


def generate_html_response(template: Template) -> HTMLResponse:
    with open(template.path_to_file, 'r') as out_file:
        html_content = out_file.read()
    return HTMLResponse(content=html_content)


@app.get('/templates/{template_id}', summary='Возвращает шаблон', tags=["templates"])
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = crud.get_template(db, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    return generate_html_response(template)


@app.get('/templates',
         response_model=list[TemplateOut],
         summary='Возвращает список всех шаблонов',
         tags=["templates"])
def get_templates(db: Session = Depends(get_db)):
    return crud.get_templates(db)


@app.put('/templates/{template_id}', response_model=TemplateOut, summary='Обновляет шаблон', tags=["templates"])
def update_template(
        template_id: int,
        template_in: TemplateIn,
        file: UploadFile = File(None),
        db: Session = Depends(get_db)
    ):
    template = crud.update_template(db, template_id, template_in)
    if template is not None:
        if file:
            if file.content_type == "text/html":
                create_html_file(file, template.path_to_file)
            else:
                raise HTTPException(status_code=400, detail="Недопустимый тип файла")
        return template
    raise HTTPException(status_code=404, detail="Шаблон не найден")


@app.delete(
    '/templates/{template_id}',
    response_model=TemplateOut,
    summary='Удаляет шаблон из базы',
    tags=["templates"]
    )
def delete_template(template_id: int, db: Session = Depends(get_db)):
    deleted_template = crud.delete_template(db, template_id)
    if deleted_template is None:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    delete_file_from_storage(deleted_template.path_to_file)
    return deleted_template


def create_path_to_file(path_to_storage: str, extension: str):
    return os.path.join(path_to_storage, str(uuid.uuid4()) + extension)


def create_html_file(file: UploadFile, path_to_file: str):
    with open(path_to_file, 'w') as out_file:
        content = file.file.read().decode()
        out_file.write(content)


def delete_file_from_storage(path_to_file: str):
    os.remove(path_to_file)
