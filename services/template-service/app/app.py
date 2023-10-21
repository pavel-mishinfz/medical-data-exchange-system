import os
import typing

from .shemas.template import Template

from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse


app = FastAPI(title='Template Service')
templates: typing.Dict[int, Template] = {}
path_to_storage = 'C:/Medical-Data-Exchange-System/storage/'


@app.post('/templates/', summary='Добавляет шаблон в базу')
def add_template(name: str, file: UploadFile):
    result = Template(
        id=len(templates)+1,
        name=name,
        path=path_to_storage + file.filename
    )
    templates[result.id] = result
    with open(result.path, 'w') as out_file:
        content = file.file.read().decode()
        out_file.write(content)
    return result


@app.get('/templates/{template_id}', summary='Возвращает шаблон')
def get_template(template_id: int):
    if template_id in templates:
        return templates[template_id]
    return JSONResponse(status_code=404, content={"message": "Шаблон не найден"})


@app.put('/templates/{template_id}', summary='Обновляет шаблон')
def update_template(template_id: int, file: UploadFile, name: str | None = None):
    if template_id in templates:
        if name is None:
            name = templates[template_id].name
        result = Template(
            id=template_id,
            name=name,
            path=path_to_storage + file.filename
        )
        with open(templates[template_id].path, 'w') as out_file:
            content = file.file.read().decode()
            out_file.write(content)
        os.rename(templates[template_id].path, result.path)
        templates[template_id] = result
        return result
    return JSONResponse(status_code=404, content={"message": "Шаблон не найден"})


@app.delete('/templates/{template_id}', summary='Удаляет шаблон из базы')
def delete_page_template(template_id: int):
    if template_id in templates:
        os.remove(templates[template_id].path)
        del templates[template_id]
        return JSONResponse(status_code=200, content={"message": "Шаблон успешно удален"})
    return JSONResponse(status_code=404, content={"message": "Шаблон не найден"})
