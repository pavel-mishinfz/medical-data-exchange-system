import os
from fastapi import FastAPI, UploadFile, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy.orm import Session
from .schemas.template import Template
from .database.database import Base, engine, SessionLocal
from . import crud


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

Base.metadata.create_all(bind=engine)

app = FastAPI(title='Template Service',
              description=description,
              openapi_tags=tags_metadata)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


path_to_storage = 'C:/Medical-Data-Exchange-System/storage/'


@app.post('/templates', summary='Добавляет шаблон в базу', tags=["templates"])
def add_template(name: str, file: UploadFile, db: Session = Depends(get_db)):
    content_type = file.content_type
    if content_type == "text/html":
        new_template = crud.create_template(db, name, path_to_storage)
        with open(new_template.path, 'w') as out_file:
            content = file.file.read().decode()
            out_file.write(content)
        return new_template
    return JSONResponse(status_code=400, content={"message": "Недопустимый тип файла"})


def generate_html_response(template: Template):
    with open(template.path, 'r') as out_file:
        html_content = out_file.read()
    return HTMLResponse(content=html_content)


@app.get('/templates/{template_id}', summary='Возвращает шаблон', tags=["templates"])
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = crud.get_template(db, template_id)
    if template is not None:
        return generate_html_response(template)
    return JSONResponse(status_code=404, content={"message": "Шаблон не найден"})


@app.get('/templates',
         response_model=list[Template],
         summary='Возвращает список всех шаблонов',
         tags=["templates"])
def get_templates(db: Session = Depends(get_db)):
    return crud.get_templates(db)


@app.put('/templates/{template_id}', summary='Обновляет шаблон', tags=["templates"])
def update_template(template_id: int, name: str, file: UploadFile, db: Session = Depends(get_db)):
    template = crud.update_template(db, template_id, name)
    if template is not None:
        content_type = file.content_type
        if content_type == "text/html":
            with open(template.path, 'w') as out_file:
                content = file.file.read().decode()
                out_file.write(content)
            return template
        return JSONResponse(status_code=400, content={"message": "Недопустимый тип файла"})
    return JSONResponse(status_code=404, content={"message": "Шаблон не найден"})


@app.delete('/templates/{template_id}', summary='Удаляет шаблон из базы', tags=["templates"])
def delete_template(template_id: int, db: Session = Depends(get_db)):
    deleted_template = crud.delete_template(db, template_id)
    if deleted_template is not None:
        os.remove(deleted_template.path)
        return deleted_template
    return JSONResponse(status_code=404, content={"message": "Шаблон не найден"})
