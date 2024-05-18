import json
import os
import pathlib
import uuid
import asyncio
from datetime import datetime, timezone, timedelta

from fastapi import Depends, FastAPI, HTTPException, UploadFile, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.ext.asyncio import AsyncSession

from . import config, users
from .users import schemas
from .users.database import database
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
 
Также данный сервис позволяет _отправить код подтверждения_ на электронную почту пользователю при смене почты.
"""

tags_metadata = [
    {
        "name": "specialization",
        "description": "Операции со специализациями врачей",
    },
]

app = FastAPI(title='User Service',
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

users.inject_secrets(
    jwt_secret=app_config.jwt_secret.get_secret_value(),
    verification_token_secret=app_config.verification_token_secret.get_secret_value(),
    reset_password_token_secret=app_config.reset_password_token_secret.get_secret_value()
)

user_router = fastapi_users.get_users_router(schemas.user.UserRead, schemas.user.UserUpdate)
new_user_router = APIRouter()

for route in user_router.routes:
    if route.methods != {"PATCH"}:
        new_user_router.routes.append(route)

app.include_router(new_user_router, prefix="/users", tags=["users"])
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


@app.get(
    "/users/specialization/{specialization_id}", response_model=list[schemas.user.UserRead],
    summary="Возвращает список врачей конкретной специализации", tags=["users"]
    )
async def get_doctors_of_specialization(
    specialization_id: int, session: AsyncSession = Depends(database.get_async_session)
    ):
    return await users.crud_user.get_doctors_of_specialization(specialization_id, session)


@app.patch(
    "/users/me/image",
    response_model=schemas.user.UserRead,
    summary='Обновляет фотографию в профиле пользователя',
    tags=['users']
    )
async def update_user_image(
    file: UploadFile,
    current_user: schemas.user.UserRead = Depends(fastapi_users.current_user(active=True, verified=True)),
    session: AsyncSession = Depends(database.get_async_session)
):
    if file.content_type not in ['image/png', 'image/jpeg']:
        raise HTTPException(status_code=400, detail="Недопустимый тип файла")
    file_path = current_user.img
    if file_path is not None:
        os.remove(file_path)
    file_path = make_path_to_file(app_config.path_to_storage, file.filename)
    make_img_file(file_path, file)
    return await users.crud_user.update_img(file_path, current_user.id, session)


@app.delete(
    "/users/me/image",
    response_model=schemas.user.UserRead,
    summary='Удаляет фотографию в профиле пользователя',
    tags=['users']
    )
async def delete_user_image(
    current_user: schemas.user.UserRead = Depends(fastapi_users.current_user(active=True, verified=True)),
    session: AsyncSession = Depends(database.get_async_session)
):
    file_path = current_user.img
    if file_path is not None:
        os.remove(file_path)
    return await users.crud_user.update_img(None, current_user.id, session)


@app.patch(
    "/users/{id}/image",
    response_model=schemas.user.UserRead,
    summary='Обновляет фотографию пользователя',
    dependencies=[Depends(fastapi_users.current_user(active=True, verified=True, superuser=True))],
    tags=['users']
    )
async def update_user_image_by_id(
    id: uuid.UUID,
    file: UploadFile,
    session: AsyncSession = Depends(database.get_async_session)
):
    user = await users.crud_user.get_user(id, session)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if file.content_type not in ['image/png', 'image/jpeg']:
        raise HTTPException(status_code=400, detail="Недопустимый тип файла")
    file_path = user.img
    if file_path is not None:
        os.remove(file_path)
    file_path = make_path_to_file(app_config.path_to_storage, file.filename)
    make_img_file(file_path, file)
    return await users.crud_user.update_img(file_path, user.id, session)


@app.delete(
    "/users/{id}/image",
    response_model=schemas.user.UserRead,
    summary='Удаляет фотографию пользователя',
    dependencies=[Depends(fastapi_users.current_user(active=True, verified=True, superuser=True))],
    tags=['users']
    )
async def delete_user_image_by_id(
    id: uuid.UUID,
    session: AsyncSession = Depends(database.get_async_session)
):
    user = await users.crud_user.get_user(id, session)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    file_path = user.img
    if file_path is not None:
        os.remove(file_path)
    return await users.crud_user.update_img(None, user.id, session)


@app.get(
    "/users/doctor/{doctor_id}/summary",
    response_model=schemas.user.DoctorRead,
    summary='Возвращает информацию о враче для пользователя',
    dependencies=[Depends(fastapi_users.current_user(active=True, verified=True))],
    tags=['users']
    )
async def get_doctor_for_patient(
    doctor_id: uuid.UUID,
    session: AsyncSession = Depends(database.get_async_session)
):
    user = await users.crud_user.get_doctor(doctor_id, session)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@app.get(
    "/users/user/{user_id}/summary",
    response_model=schemas.user.UserReadSummary,
    summary='Возвращает основную информацию о пользователе для врача',
    dependencies=[Depends(fastapi_users.current_user(active=True, verified=True))],
    tags=['users']
    )
async def get_patient_for_doctor(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(database.get_async_session)
):
    user = await users.crud_user.get_user(user_id, session)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@app.patch(
    "/users/me",
    response_model=schemas.user.UserRead,
    summary='Обновляет основную информацию о текущем пользователе',
    tags=['users']
    )
async def update_current_user_overload(
    user: schemas.user.UserUpdate,
    current_user: schemas.user.UserRead = Depends(fastapi_users.current_user(active=True, verified=True)),
    session: AsyncSession = Depends(database.get_async_session)
):
    updated_user = await users.crud_user.update_user(current_user.id, user, session)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return updated_user


@app.patch(
    "/users/{id}",
    response_model=schemas.user.UserRead,
    summary='Обновляет основную информацию о пользователе по id',
    dependencies=[Depends(fastapi_users.current_user(active=True, verified=True, superuser=True))],
    tags=['users']
    )
async def update_user_overload(
    id: uuid.UUID,
    user: schemas.user.UserUpdate,
    session: AsyncSession = Depends(database.get_async_session)
):
    updated_user = await users.crud_user.update_user(id, user, session)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return updated_user


@app.patch(
    "/users/me/email",
    response_model=schemas.user.UserRead,
    summary='Обновляет почту текущего пользователя',
    tags=['users']
    )
async def update_current_user_email(
    email: str,
    current_user: schemas.user.UserRead = Depends(fastapi_users.current_user(active=True, verified=True)),
    session: AsyncSession = Depends(database.get_async_session)
):
    date = datetime.now(timezone.utc)
    confirm_code = await users.crud_confirm_code.get_confirm_code(session, current_user.id)
    if confirm_code is None:
        raise HTTPException(status_code=403, detail="Изменение почты недоступно")
    if not confirm_code.activation_time or (date - confirm_code.activation_time).seconds > 900: 
        raise HTTPException(status_code=403, detail="Изменение почты недоступно")
    updated_user = await users.crud_user.update_user_email(current_user.id, email, session)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    await users.crud_confirm_code.delete_confirm_code(session, current_user.id)
    return updated_user


@app.patch(
    "/users/{user_id}/email",
    response_model=schemas.user.UserRead,
    summary='Обновляет почту пользователя по id',
    tags=['users']
    )
async def update_user_email(
    email: str,
    user_id: uuid.UUID,
    current_user: schemas.user.UserRead = Depends(fastapi_users.current_user(active=True, verified=True, superuser=True)),
    session: AsyncSession = Depends(database.get_async_session)
):
    date = datetime.now(timezone.utc)
    confirm_code = await users.crud_confirm_code.get_confirm_code(session, current_user.id)
    if confirm_code is None:
        raise HTTPException(status_code=403, detail="Изменение почты недоступно")
    if not confirm_code.activation_time or (date - confirm_code.activation_time).seconds > 900: 
        raise HTTPException(status_code=403, detail="Изменение почты недоступно")
    updated_user = await users.crud_user.update_user_email(user_id, email, session)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    await users.crud_confirm_code.delete_confirm_code(session, current_user.id)
    return updated_user


@app.get(
    "/users", response_model=list[schemas.user.UserRead],
    summary="Возвращает список всех пользователей",
    dependencies=[Depends(fastapi_users.current_user(active=True, verified=True, superuser=True))],
    tags=["users"]
    )
async def get_list_users(
    session: AsyncSession = Depends(database.get_async_session)
    ):
    return await users.crud_user.get_users_list(session)


@app.get(
    "/users/patients", response_model=list[schemas.user.UserReadSummary],
    summary="Возвращает список всех пациентов",
    dependencies=[Depends(fastapi_users.current_user(active=True, verified=True))],
    tags=["users"]
    )
async def get_list_patients(
    session: AsyncSession = Depends(database.get_async_session)
    ):
    return await users.crud_user.get_users_list(session, group_id=3)


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
         response_model=schemas.specialization.Specialization,
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
           response_model=schemas.specialization.Specialization,
           summary='Обновляет информацию о специализации',
           tags=['specialization'])
async def update_specialization(
    specialization_id: int,
    specialization: schemas.specialization.SpecializationOptional,
    session: AsyncSession = Depends(database.get_async_session)
    ):

    specialization = await users.crud_specialization.update_specialization(
        session, specialization_id, specialization
    )
    if specialization is not None:
        return specialization
    return HTTPException(status_code=404, detail="Специализация не найдена")


@app.delete("/specializations/{specialization_id}",
            response_model=schemas.specialization.Specialization,
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
    "/send_confirm_code", status_code=201,
    summary='Создает новый код подтвержения',
    tags=['confirm_code']
)
async def add_confirm_code(
    current_user: schemas.user.UserRead = Depends(fastapi_users.current_user(active=True, verified=True)),
    session: AsyncSession = Depends(database.get_async_session)
):
    confirm_code = await users.crud_confirm_code.upsert_confirm_code(session, current_user.id)
    message = make_template_change_email(code=confirm_code.code)
    await users.usermanager.send_email(message=message, subject='Изменение почты', to=current_user.email)


@app.post(
    "/check_confirm_code", status_code=201,
    summary='Проверяет код подтвержения',
    tags=['confirm_code']
)
async def check_confirm_code(
    code: str,
    current_user: schemas.user.UserRead = Depends(fastapi_users.current_user(active=True, verified=True)),
    session: AsyncSession = Depends(database.get_async_session)
):
    date = datetime.now(timezone.utc)
    correct_code = await users.crud_confirm_code.get_confirm_code(session, current_user.id)
    if correct_code is None:
        raise HTTPException(status_code=404, detail="Код не найден")
    if (date - correct_code.create_date).seconds > 180:
        raise HTTPException(status_code=404, detail="Код истек")
    if code != correct_code.code:
        raise HTTPException(status_code=404, detail="Неверный код")
    await users.crud_confirm_code.activate_code(current_user.id, date, session)


@app.on_event("startup")
async def on_startup():
    await database.DB_INITIALIZER.init_database(
        app_config.postgres_dsn_async.unicode_string()
    )

    groups = []
    with open(app_config.default_groups_config_path, encoding="utf-8") as f:
        groups = json.load(f)   

    async for session in database.get_async_session():
        for group in groups:
            await users.groupcrud.upsert_group(
                session, schemas.group.GroupUpsert(**group)
            )

    specializations = []
    with open(app_config.default_specializations_config_path, encoding="utf-8") as f:
        specializations = json.load(f) 

    async for session in database.get_async_session():
        for specialization in specializations:
            await users.crud_specialization.upsert_specialization(
                session, schemas.specialization.SpecializationUpsert(**specialization)
            )

    asyncio.create_task(delete_old_confirmation_codes())        


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


def make_template_change_email(code: str):
    return f"""
    <html>
        <body>
            <div style="background-color:#fff;padding:20px">
                <h1>Код подтверждения</h1>
                <p style="display:block;font-size:24px;padding:10px;width: 80px;
                border-radius: 15px;background-color: #d2cece;">
                    {code}
                </p>
            </div>
        </body>
    </html>
    """

async def delete_old_confirmation_codes():
    async for session in database.get_async_session():
        while True:
            date = datetime.now()
            expired_time = date - timedelta(seconds=180)
            expired_activation_time = date - timedelta(seconds=900)
            codes_to_delete = await users.crud_confirm_code.get_old_confirm_codes(session, expired_time, expired_activation_time)
            for code in codes_to_delete:
                await users.crud_confirm_code.delete_confirm_code(session, code.user_id)
            await asyncio.sleep(60)