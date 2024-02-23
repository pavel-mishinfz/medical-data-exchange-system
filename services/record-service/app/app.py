import uuid

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import Record, RecordIn, RecordOptional
from .database import DB_INITIALIZER, get_async_session
from . import crud, config

description = """"""

tags_metadata = [
    {
        "name": "records",
        "description": "Операции с записями пациентов на прием",
    }
]

cfg: config.Config = config.load_config()

app = FastAPI(title='Record Service',
              description=description,
              openapi_tags=tags_metadata)


@app.post(
    '/records',
    response_model=Record,
    summary='Добавляет новую запись пациента на прием в базу',
    tags=["records"]
)
async def add_record(record_in: RecordIn, db: AsyncSession = Depends(get_async_session)):
    return await crud.create_record(db, record_in)


@app.get(
    '/records/{record_id}',
    response_model=Record,
    summary='Возвращает запись пациента',
    tags=["records"]
)
async def get_record(record_id: int, db: AsyncSession = Depends(get_async_session)):
    record = await crud.get_record(db, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return record


@app.get(
    '/records/user/{user_id}',
    response_model=list[Record],
    summary='Возвращает все записи пользователя на приемы',
    tags=["records"]
)
async def get_record(user_id: uuid.UUID, db: AsyncSession = Depends(get_async_session)):
    return await crud.get_record_list(db, user_id)


@app.patch(
    '/records/{record_id}',
    response_model=Record,
    summary='Обновляет запись пациента на прием',
    tags=["records"]
)
async def update_record(
        record_id: int,
        record_optional: RecordOptional,
        db: AsyncSession = Depends(get_async_session)
):
    record = await crud.update_record(db, record_id, record_optional)
    if record is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return record


@app.delete(
    '/records/{record_id}',
    summary='Удаляет запись пациента из базы',
    response_model=Record,
    tags=["records"]
)
async def delete_record(record_id: int, db: AsyncSession = Depends(get_async_session)):
    deleted_record = await crud.delete_record(db, record_id)
    if deleted_record is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return deleted_record


@app.on_event("startup")
async def on_startup():
    await DB_INITIALIZER.init_database(
        cfg.postgres_dsn_async.unicode_string()
    )

    # loading default-time-record.json
