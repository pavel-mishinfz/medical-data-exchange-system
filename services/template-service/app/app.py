import os
from fastapi import FastAPI, UploadFile, Depends, HTTPException, Body, File
from fastapi.responses import HTMLResponse
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
SessionLocal = DB_INITIALIZER.init_database(cfg.postgres_dsn)

app = FastAPI(title='Template Service',
              description=description,
              openapi_tags=tags_metadata)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/templates', response_model=TemplateOut, summary='Добавляет шаблон в базу', tags=["templates"])
def add_template(template_in: TemplateIn = Body(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    content_type = file.content_type
    if content_type == "text/html":
        new_template = crud.create_template(db, template_in, cfg.path_to_storage)
        with open(new_template.path, 'w') as out_file:
            content = file.file.read().decode()
            out_file.write(content)
        return new_template
    raise HTTPException(status_code=400, detail="Недопустимый тип файла")


def generate_html_response(template: Template) -> HTMLResponse:
    with open(template.path, 'r') as out_file:
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
        file: UploadFile,
        db: Session = Depends(get_db)
    ):
    template = crud.update_template(db, template_id, template_in)
    if template is not None:
        content_type = file.content_type
        if content_type == "text/html":
            with open(template.path, 'w') as out_file:
                content = file.file.read().decode()
                out_file.write(content)
            return template
        raise HTTPException(status_code=400, detail="Недопустимый тип файла")
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
    os.remove(deleted_template.path)
    return deleted_template
