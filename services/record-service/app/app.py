import locale
import uuid
import datetime
import asyncio

from fastapi import FastAPI, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import (Record,
                      RecordIn,
                      RecordOptional,
                      ScheduleIn,
                      Schedule,
                      ScheduleOptional)
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
    record_exists = await crud.check_record(db, record_in)
    if record_exists:
        raise HTTPException(status_code=500, detail="Запись уже существует")
    available_dates_and_times = await get_available_dates_and_times(record_in.id_doctor, db)
    times_list = available_dates_and_times.get(record_in.date)
    if times_list is None or record_in.time not in times_list:
        raise HTTPException(status_code=403, detail="Запись недоступна")
    return await crud.create_record(db, record_in)


@app.get(
    '/records',
    response_model=list[Record],
    summary='Возвращает все записи',
    tags=["records"]
)
async def get_records_list(db: AsyncSession = Depends(get_async_session)):
    return await crud.get_records_all(db)


@app.get(
    '/records/user/{user_id}',
    response_model=list[Record],
    summary='Возвращает список записей пользователя',
    tags=["records"]
)
async def get_records_list(user_id: uuid.UUID, db: AsyncSession = Depends(get_async_session)):
    return await crud.get_records_list(db=db, user_id=user_id)


@app.delete(
    '/records/{record_id}',
    summary='Удаляет запись пациента из базы',
    response_model=Record,
    tags=["records"]
)
async def delete_record(record_id: uuid.UUID, db: AsyncSession = Depends(get_async_session)):
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
    '/schedules/doctor/{doctor_id}',
    response_model=Schedule,
    summary='Возвращает график работы',
    tags=["schedules"]
)
async def get_schedule(doctor_id: uuid.UUID, db: AsyncSession = Depends(get_async_session)):
    schedule = await crud.get_schedule(db, doctor_id=doctor_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="График не найден")
    return schedule


@app.get(
    '/schedules/doctor/{doctor_id}/available_dates',
    response_model=dict,
    summary='Возвращает доступные даты для записи на прием',
    tags=["schedules"]
)
async def get_available_dates_of_doctor(doctor_id: uuid.UUID, db: AsyncSession = Depends(get_async_session)):
    return await get_available_dates_and_times(doctor_id, db)


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


@app.on_event("startup")
async def on_startup():
    await DB_INITIALIZER.init_database(
        cfg.postgres_dsn_async.unicode_string()
    )

    asyncio.create_task(delete_old_records())


async def get_available_dates_and_times(
        doctor_id: uuid.UUID,
        db: AsyncSession = Depends(get_async_session)
    ):
    model_schedule = await crud.get_schedule(db, doctor_id=doctor_id)
    if model_schedule is None:
        raise HTTPException(status_code=404, detail="График не найден")
    schedule = dict(model_schedule.schedule)
    records = await get_records(db, model_schedule.id_doctor)
    available_dates = await make_available_dates(schedule)
    available_dates_and_times = await make_available_dates_and_times(
        records, available_dates, schedule, model_schedule.time_per_patient
    )
    return available_dates_and_times


async def convert_string_to_time(string):
    return datetime.datetime.strptime(string, "%H:%M")


async def get_records(db, id_doctor):
    records = {}
    list_model_record = await crud.get_records_list(db=db, doctor_id=id_doctor)
    for model_record in list_model_record:
        model_record = model_record.__dict__
        date = model_record['date']
        time = await convert_string_to_time(model_record['time'])
        if date in records.keys():
            records[date].append(time)
        else:
            records[date] = [time]
    return records


async def make_current_and_deadline_dates():
    current_date = datetime.date.today()
    deadline_date = current_date + datetime.timedelta(days=14)
    return current_date, deadline_date


async def make_available_dates(schedule):
    current_date, deadline_date = await make_current_and_deadline_dates()

    available_dates = {}
    while current_date <= deadline_date:
        weekday = current_date.weekday().__str__()
        date = current_date
        available_dates[date] = weekday
        current_date += datetime.timedelta(days=1)
    return available_dates


async def make_start_and_end_times(left_boundary_time, right_boundary_time):
    start_time = await convert_string_to_time(left_boundary_time)
    end_time = await convert_string_to_time(right_boundary_time)
    return start_time, end_time


async def make_list_available_times(time, time_per_patient, list_unavailable_times):
    available_times = []
    left_boundary_time, right_boundary_time = time.split('-')
    start_time, end_time = await make_start_and_end_times(left_boundary_time, right_boundary_time)
    while start_time <= end_time:
        if list_unavailable_times is None or start_time not in list_unavailable_times:
            available_times.append(start_time.strftime("%H:%M"))
        start_time += datetime.timedelta(minutes=time_per_patient)
    return available_times


async def make_available_dates_and_times(records, available_dates, schedule, time_per_patient):
    available_dates_and_times = {}
    for date, weekday in available_dates.items():
        time = schedule.get(weekday)
        if time is None:
            available_dates_and_times[date] = []    
        else:
            list_unavailable_times = records.get(date)
            available_dates_and_times[date] = await make_list_available_times(
                time, time_per_patient, list_unavailable_times
            )
    return available_dates_and_times


async def delete_old_records():
    async for session in get_async_session():
        while True:
            records_to_delete = await crud.get_old_records(session)
            for record in records_to_delete:
                await crud.delete_record(session, record.id)
            await asyncio.sleep(24 * 60 * 60)
            