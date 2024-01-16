from email.mime.text import MIMEText
from smtplib import SMTP_SSL

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from . import config, users
from .users import schemas
from .users.database import database


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
 
Также данный сервис позволяет _отправить сообщение_ на электронную почту пользователю 
для подтверждения аккаунта или сброса пароля.
"""

tags_metadata = [
    {
        "name": "email",
        "description": "Отправка сообщения пользователю",
    }
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
async def delete_device(
    group_id: int,
    session: AsyncSession = Depends(database.get_async_session)
    ):

    group = await users.groupcrud.get_group(session, group_id)
    if await users.groupcrud.delete_group(session, group_id):
        return group
    return HTTPException(status_code=404, detail="Группа не найдена")


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
        app_config.postgres_dsn.unicode_string()
    )
