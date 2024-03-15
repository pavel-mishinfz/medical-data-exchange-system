import json
import os
import pathlib
import shutil
import uuid
from email.mime.text import MIMEText
from smtplib import SMTP_SSL

from fastapi import Depends, FastAPI, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from . import config, users
from .users import schemas
from .users.database import database, models
from .users.userapp import fastapi_users


app_config: config.Config = config.load_config()

description = """
Сервис предназначен для: 

* **получение/обновления текущего пользователя** 
* **получения/обновления конкретного пользователя**
* **удаления пользователя конкретного пользователя**
* **создания новой группы пользователей**
* **получения всех групп пользователей**
* **получения информации о группе пользователей**
* **обновления информации о группе пользователей**
* **удаления информации о группе пользователей**

Для _пользователя_ имееются следующие маршруты:

* **Войти** 
* **Выйти**
* **Регистрация** 
* **Получение токена для сброса пароля**
* **Сброс пароля**
* **Получение токена для подтверждения аккаунта**
* **Подтверждение аккаунта**

Для аутентификации используется заголовок **Authorization: Bearer** + **JWT**
 
Сервис предоставляет CRUD для специализаций врачей.
 
Также данный сервис позволяет _отправить сообщение_ на электронную почту пользователю 
для подтверждения аккаунта или сброса пароля.
"""

tags_metadata = [
    {
        "name": "email",
        "description": "Отправка сообщения пользователю",
    },
    {
        "name": "specialization",
        "description": "Операции со специализациями врачей",
    },
]

app = FastAPI(title='User Service',
              description=description,
              openapi_tags=tags_metadata)

users.inject_secrets(
    jwt_secret=app_config.jwt_secret.get_secret_value(),
    verification_token_secret=app_config.verification_token_secret.get_secret_value(),
    reset_password_token_secret=app_config.reset_password_token_secret.get_secret_value()
)
users.include_routers(app)


@app.post(
    "/groups", status_code=201,
    response_model=schemas.group.GroupRead,
    summary='Создает новую группу пользователей',
    tags=['user-groups']
    )
async def add_group(
    group: schemas.group.GroupCreate,
    session: AsyncSession = Depends(database.get_async_session)
    ):

    return await users.groupcrud.create_group(group, session)


@app.get(
    "/groups",
    summary='Возвращает список групп пользователей',
    response_model=list[schemas.group.GroupRead],
    tags=['user-groups']
    )
async def get_group_list(
    session: AsyncSession = Depends(database.get_async_session),
    skip: int = 0,
    limit: int = 100
    ):

    return await users.groupcrud.get_groups(session, skip, limit)


@app.get("/groups/{group_id}", summary='Возвращает информацию о группе пользователей', tags=['user-groups'])
async def get_group_info(
    group_id: int, session: AsyncSession = Depends(database.get_async_session)
    ):

    group = await users.groupcrud.get_group(session, group_id)
    if group is not None:
        return group
    return HTTPException(status_code=404, detail="Группа не найдена")


@app.put("/groups/{group_id}", summary='Обновляет информацию о группе пользователей', tags=['user-groups'])
async def update_group(
    group_id: int,
    group: schemas.group.GroupUpdate,
    session: AsyncSession = Depends(database.get_async_session)
    ):

    group = await users.groupcrud.update_group(session, group_id, group)
    if group is not None:
        return group
    return HTTPException(status_code=404, detail="Группа не найдена")


@app.delete("/groups/{group_id}", summary='Удаляет информацию о группе пользователей', tags=['user-groups'])
async def delete_group(
    group_id: int,
    session: AsyncSession = Depends(database.get_async_session)
    ):

    group = await users.groupcrud.get_group(session, group_id)
    if await users.groupcrud.delete_group(session, group_id):
        return group
    return HTTPException(status_code=404, detail="Группа не найдена")


@app.patch(
    "/users/me/img",
    response_model=schemas.user.UserRead,
    summary='Обновляет фотографию в профиле пользователя',
    tags=['users']
    )
async def update_img_user(
    file: UploadFile,
    current_user: schemas.user.UserRead = Depends(fastapi_users.current_user(active=True)),
    session: AsyncSession = Depends(database.get_async_session)
    ):
    if file.content_type in ['image/png', 'image/jpeg']:
        path_to_file = current_user.img
        if path_to_file is None:
            path_to_file = make_path_to_file(app_config.path_to_storage, file.filename)
        make_img_file(path_to_file, file)
        return await users.crud_user.update_img(path_to_file, current_user.id, session)
    raise HTTPException(status_code=400, detail="Недопустимый тип файла")


@app.delete(
    "/users/me/img",
    response_model=schemas.user.UserRead,
    summary='Удаляет фотографию в профиле пользователя',
    tags=['users']
    )
async def delete_img_user(
    current_user: schemas.user.UserRead = Depends(fastapi_users.current_user(active=True)),
    session: AsyncSession = Depends(database.get_async_session)
    ):
    img = current_user.img
    if img is not None:
        os.remove(img)
    return await users.crud_user.update_img(None, current_user.id, session)


@app.get(
    "/users", response_model=list[schemas.user.UserRead],
    summary="Возвращает список всех пользователей", tags=["users"]
    )
async def get_list_users(
    session: AsyncSession = Depends(database.get_async_session)
    ):

    result = await session.execute(select(models.User))
    return result.scalars().all()


@app.post(
    "/specializations",
    response_model=schemas.specialization.Specialization,
    summary='Создает новую специализацию',
    tags=['specialization']
    )
async def add_specialization(
    specialization: schemas.specialization.SpecializationIn,
    session: AsyncSession = Depends(database.get_async_session)
    ):

    return await users.crud_specialization.create_specialization(specialization, session)


@app.get(
    "/specializations",
    summary='Возвращает список специализаций',
    response_model=list[schemas.specialization.Specialization],
    tags=['specialization']
    )
async def get_specialization_list(
    session: AsyncSession = Depends(database.get_async_session),
    skip: int = 0,
    limit: int = 100
    ):

    return await users.crud_specialization.get_specialization_list(session, skip, limit)


@app.get("/specializations/{specialization_id}",
         summary='Возвращает информацию о специализации',
         tags=['specialization'])
async def get_specialization(
    specialization_id: int, session: AsyncSession = Depends(database.get_async_session)
    ):

    specialization = await users.crud_specialization.get_specialization(session, specialization_id)
    if specialization is not None:
        return specialization
    return HTTPException(status_code=404, detail="Специализация не найдена")


@app.patch("/specializations/{specialization_id}",
           summary='Обновляет информацию о специализации',
           tags=['specialization'])
async def update_specialization(
    specialization_id: int,
    specialization: schemas.specialization.SpecializationOptional,
    session: AsyncSession = Depends(database.get_async_session)
    ):

    specialization = await users.crud_specialization.update_specialization(session, specialization_id, specialization)
    if specialization is not None:
        return specialization
    return HTTPException(status_code=404, detail="Специализация не найдена")


@app.delete("/specializations/{specialization_id}",
            summary='Удаляет информацию о специализации',
            tags=['specialization'])
async def delete_specialization(
    specialization_id: int,
    session: AsyncSession = Depends(database.get_async_session)
    ):

    specialization = await users.crud_specialization.get_specialization(session, specialization_id)
    if await users.crud_specialization.delete_specialization(session, specialization_id):
        return specialization
    return HTTPException(status_code=404, detail="Специализация не найдена")


@app.post(
    "/email",
    summary='Отправляет сообщение для подтверждения аккаунта или сброса пароля',
    tags=['email']
    )
async def send_email(body: schemas.mail.EmailBody):
    msg = MIMEText(body.message, "html")
    msg['Subject'] = body.subject
    msg['From'] = f'<{app_config.own_email}>'
    msg['To'] = body.to

    with SMTP_SSL("smtp.gmail.com", port=465) as server:
        server.login(app_config.own_email, app_config.own_email_password)
        server.send_message(msg)
        server.quit()
        return {"message": "Сообщение успешно отправлено"}


@app.on_event("startup")
async def on_startup():
    await database.DB_INITIALIZER.init_database(
        app_config.postgres_dsn_async.unicode_string()
    )

    groups = []
    with open(app_config.default_groups_config_path) as f:
        groups = json.load(f)

    async for session in database.get_async_session():
        for group in groups:
            await users.groupcrud.upsert_group(
                session, schemas.group.GroupUpsert(**group)
            )


def make_path_to_file(path_to_storage, file_name):
    extension = pathlib.Path(file_name).suffix
    path_to_file = os.path.join(path_to_storage, str(uuid.uuid4()) + extension)
    return path_to_file


def make_img_file(path_to_file, file):
    try:
        with open(path_to_file, 'wb') as out_file:
            out_file.write(file.file.read())
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка при работе с файлом")
