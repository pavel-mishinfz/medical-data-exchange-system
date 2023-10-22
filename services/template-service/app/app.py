import os
import typing

from shemas import Template

from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse


app = FastAPI(title='Template Service')
templates: typing.Dict[int, Template] = {}
path_to_storage = 'C:/Medical-Data-Exchange-System/storage/'


@app.post('/templates', summary='Добавляет шаблон в базу')
def add_template(name: str, file: UploadFile):
    id_file = len(templates)+1
    result = Template(
        id=id_file,
        name=name,
        path=path_to_storage + str(id_file) + '.html'
    )
    templates[result.id] = result
    with open(result.path, 'w') as out_file:
        content = file.file.read().decode()
        out_file.write(content)
    return result


def generate_html_response(template_id):
    with open(templates[template_id].path, 'r') as out_file:
        html_content = out_file.read()
    return HTMLResponse(content=html_content)


@app.get('/templates/{template_id}', summary='Возвращает шаблон')
def get_template(template_id: int):
    if template_id in templates:
        return generate_html_response(template_id)
    return JSONResponse(status_code=404, content={"message": "Шаблон не найден"})


@app.get('/templates', summary='Возвращает список всех шаблонов')
def get_template():
    return [{'id': v.id, 'name': v.name} for k, v in templates.items()]


@app.put('/templates/{template_id}', summary='Обновляет шаблон')
def update_template(template_id: int, name: str, file: UploadFile):
    if template_id in templates:
        result = Template(
            id=template_id,
            name=name,
            path=path_to_storage + str(template_id) + '.html'
        )
        with open(templates[template_id].path, 'w') as out_file:
            content = file.file.read().decode()
            out_file.write(content)
        templates[template_id] = result
        return templates[template_id]
    return JSONResponse(status_code=404, content={"message": "Шаблон не найден"})


@app.delete('/templates/{template_id}', summary='Удаляет шаблон из базы')
def delete_page_template(template_id: int):
    if template_id in templates:
        os.remove(templates[template_id].path)
        result = templates[template_id]
        del templates[template_id]
        return result
    return JSONResponse(status_code=404, content={"message": "Шаблон не найден"})
