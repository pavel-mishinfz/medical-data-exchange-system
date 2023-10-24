import os
import typing

from .schemas import Template, TemplateBase

from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse

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

app = FastAPI(title='Template Service',
              description=description,
              openapi_tags=tags_metadata)
templates: typing.Dict[int, Template] = {}
path_to_storage = 'C:/Medical-Data-Exchange-System/storage/'


@app.post('/templates', summary='Добавляет шаблон в базу', tags=["templates"])
def add_template(name: str, file: UploadFile):
    content_type = file.content_type
    if content_type == "text/html":
        id_file = len(templates)+1
        result = Template(
            id=id_file,
            name=name,
            path=os.path.join(path_to_storage, str(id_file) + '.html')
        )
        templates[result.id] = result
        with open(result.path, 'w') as out_file:
            content = file.file.read().decode()
            out_file.write(content)
        return TemplateBase(id=templates[result.id].id, name=templates[result.id].name)
    return JSONResponse(status_code=400, content={"message": "Недопустимый тип файла"})


def generate_html_response(template_id):
    with open(templates[template_id].path, 'r') as out_file:
        html_content = out_file.read()
    return HTMLResponse(content=html_content)


@app.get('/templates/{template_id}', summary='Возвращает шаблон', tags=["templates"])
def get_template(template_id: int):
    if template_id in templates:
        return generate_html_response(template_id)
    return JSONResponse(status_code=404, content={"message": "Шаблон не найден"})


@app.get('/templates', response_model=list[TemplateBase], summary='Возвращает список всех шаблонов', tags=["templates"])
def get_template():
    return [TemplateBase(id=v.id, name=v.name) for k, v in templates.items()]


@app.put('/templates/{template_id}', summary='Обновляет шаблон', tags=["templates"])
def update_template(template_id: int, name: str, file: UploadFile):
    if template_id in templates:
        content_type = file.content_type
        if content_type == "text/html":
            result = Template(
                id=template_id,
                name=name,
                path=os.path.join(path_to_storage, str(template_id) + '.html')
            )
            with open(templates[template_id].path, 'w') as out_file:
                content = file.file.read().decode()
                out_file.write(content)
            templates[template_id] = result
            return templates[template_id]
        return JSONResponse(status_code=400, content={"message": "Недопустимый тип файла"})
    return JSONResponse(status_code=404, content={"message": "Шаблон не найден"})


@app.delete('/templates/{template_id}', summary='Удаляет шаблон из базы', tags=["templates"])
def delete_template(template_id: int):
    if template_id in templates:
        os.remove(templates[template_id].path)
        result = templates[template_id]
        del templates[template_id]
        return TemplateBase(id=result.id, name=result.name)
    return JSONResponse(status_code=404, content={"message": "Шаблон не найден"})
