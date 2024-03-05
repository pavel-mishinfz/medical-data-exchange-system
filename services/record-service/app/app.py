import locale
import uuid
import datetime

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import Record, RecordIn, RecordOptional, RecordForUser, ScheduleIn, Schedule, ScheduleOptional
from .database import DB_INITIALIZER, get_async_session
from . import crud, config

description = """"""

tags_metadata = [
    {
        "name": "records",
        "description": "Операции с записями пациентов на прием",
    },
    {
        "name": "schedules",
        "description": "Операции с графиками работы врачей"
    }
]

cfg: config.Config = config.load_config()

app = FastAPI(title='Record Service',
              description=description,
              openapi_tags=tags_metadata)

locale.setlocale(locale.LC_ALL, '')


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
    response_model=list[RecordForUser],
    summary='Возвращает список записи на приемы для пациента',
    tags=["records"]
)
async def get_record(user_id: uuid.UUID, db: AsyncSession = Depends(get_async_session)):
    return await crud.get_record_list_for_patient(db, user_id)


@app.get(
    '/records/doctor/{doctor_id}',
    response_model=list[Record],
    summary='Возвращает список записей пользователей для врача',
    tags=["records"]
)
async def get_record(doctor_id: uuid.UUID, db: AsyncSession = Depends(get_async_session)):
    return await crud.get_record_list_for_doctor(db, doctor_id)


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


@app.post("/schedules",
          response_model=Schedule,
          summary='Создает график работы врача',
          tags=["schedules"]
          )
async def add_schedule(schedule_in: ScheduleIn, db: AsyncSession = Depends(get_async_session)):
    return await crud.create_schedule(db, schedule_in)


@app.get(
    '/schedules/{schedule_id}',
    response_model=Schedule,
    summary='Возвращает график работы врача',
    tags=["schedules"]
)
async def get_schedule(schedule_id: int, db: AsyncSession = Depends(get_async_session)):
    schedule = await crud.get_schedule(db, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="График не найден")
    return schedule


@app.patch(
    '/schedules/{schedule_id}',
    response_model=Schedule,
    summary='Обновляет график работы врача',
    tags=["schedules"]
)
async def update_schedule(
        schedule_id: int,
        schedule_optional: ScheduleOptional,
        db: AsyncSession = Depends(get_async_session)
):
    schedule = await crud.update_schedule(db, schedule_id, schedule_optional)
    if schedule is None:
        raise HTTPException(status_code=404, detail="График не найден")
    return schedule


@app.delete(
    '/schedules/{schedule_id}',
    summary='Удаляет график работы врача из базы',
    response_model=Schedule,
    tags=["schedules"]
)
async def delete_schedule(schedule_id: int, db: AsyncSession = Depends(get_async_session)):
    deleted_schedule = await crud.delete_schedule(db, schedule_id)
    if deleted_schedule is None:
        raise HTTPException(status_code=404, detail="График не найден")
    return deleted_schedule


@app.get(
    '/schedules/{schedule_id}/dates',
    response_model=dict,
    summary='Возвращает доступные для записи даты и время',
    tags=["schedules"]
)
async def get_available_dates_and_times(schedule_id: int, db: AsyncSession = Depends(get_async_session)):
    model_schedule = await crud.get_schedule(db, schedule_id)
    if model_schedule is None:
        raise HTTPException(status_code=404, detail="График не найден")
    schedule = dict(model_schedule.schedule)
    available_dates = await make_available_dates(schedule)
    available_dates_and_times = await make_available_dates_and_times(
        available_dates, schedule, model_schedule.time_per_patient
    )
    return available_dates_and_times


@app.on_event("startup")
async def on_startup():
    await DB_INITIALIZER.init_database(
        cfg.postgres_dsn_async.unicode_string()
    )


async def make_current_and_deadline_dates():
    current_date = datetime.datetime.today()
    deadline_date = current_date + datetime.timedelta(days=30)
    return current_date, deadline_date


async def make_available_dates(schedule):
    current_date, deadline_date = await make_current_and_deadline_dates()

    available_dates = {}
    while current_date <= deadline_date:
        weekday = current_date.weekday().__str__()
        if schedule.get(weekday):
            date = current_date.strftime("%a. %d.%m")
            available_dates[date] = weekday
        current_date += datetime.timedelta(days=1)
    return available_dates


async def make_start_and_end_times(left_boundary_time, right_boundary_time):
    start_time = datetime.datetime.strptime(left_boundary_time, "%H:%M")
    end_time = datetime.datetime.strptime(right_boundary_time, "%H:%M")
    return start_time, end_time


async def make_list_available_times(time, time_per_patient):
    available_times = []
    left_boundary_time, right_boundary_time = time.split('-')
    start_time, end_time = await make_start_and_end_times(left_boundary_time, right_boundary_time)
    while start_time <= end_time:
        available_times.append(start_time.strftime("%H:%M"))
        start_time += datetime.timedelta(minutes=time_per_patient)
    return available_times


async def make_available_dates_and_times(available_dates, schedule, time_per_patient):
    available_dates_and_times = {}
    for date, weekday in available_dates.items():
        time = schedule.get(weekday)
        available_dates_and_times[date] = await make_list_available_times(time, time_per_patient)
    return available_dates_and_times
