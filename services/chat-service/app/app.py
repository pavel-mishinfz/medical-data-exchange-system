import base64
import json
import os
import pathlib
import uuid
import requests
from cryptography.fernet import Fernet

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles

from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import Chat, ChatIn, Message, MessageIn, MessageUpdate, MessageDocument
from . import schemas
from . import crud
from . import config
from . import database

from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware


EXTENSIONS = {
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/x-zip-compressed": ".zip",
    "image/png": ".png",
    "image/jpeg": ".jpg"
}

app_config: config.Config = config.load_config()

app = FastAPI(title='Chat Service')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешите запросы с любых источников
    allow_credentials=True,
    allow_methods=["*"],  # Разрешите все HTTP-методы
    allow_headers=["*"],  # Разрешите все заголовки
)

CIPHER_SUITE: Fernet = Fernet(
    base64.b64decode(app_config.encrypt_key.get_secret_value())
)

ROOT_SERVICE_DIR = pathlib.Path(__file__).parent.parent.resolve()
app.mount("/storage", StaticFiles(directory=os.path.join(ROOT_SERVICE_DIR, "storage")), name="storage")

room_managers = {}

auth_token_url = 'https://zoom.us/oauth/token'
api_base_url = "https://api.zoom.us/v2"


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message_in: MessageIn, files: list):
        message = await self.add_messages_to_database(message_in)
        for file in files:
            await self.add_files_to_database(message.id, file)
        data = {
            'id': str(message.id),
            'sender_id': str(message.sender_id),
            'send_date': message.send_date.isoformat(),
            'message': message.message,
            'documents': files
        }
        for connection in self.active_connections:
            await connection.send_text(json.dumps(data))

    @staticmethod
    async def add_messages_to_database(message: MessageIn):
        async for async_session in database.get_async_session():
            created_message = await crud.create_message(async_session, message)
            created_message.message = CIPHER_SUITE.decrypt(created_message.message).decode()
            return created_message

    @staticmethod
    async def add_files_to_database(message_id: uuid.UUID, file: dict):
        async for async_session in database.get_async_session():
            await crud.create_file(async_session, message_id, file['name'], file['path_to_file'])        


@app.websocket("/ws/{chat_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, client_id: uuid.UUID):
    if chat_id not in room_managers:
        room_managers[chat_id] = ConnectionManager()

    manager = room_managers[chat_id]

    await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            await manager.broadcast(MessageIn(message=data['message'], chat_id=chat_id, sender_id=client_id), data['files'])
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        
# templates = Jinja2Templates(directory="app/templates")
# @app.get("/chat", tags=["chat"])
# def get_chat_page(request: Request):
#     return templates.TemplateResponse("chat.html", {"request": request})


@app.post(
        "/chats",
        tags=["chat"], 
        response_model=Chat,
        summary='Создает чат')
async def add_chat(chat: ChatIn, session: AsyncSession = Depends(database.get_async_session)) -> Chat:
    return await crud.create_chat(session, chat)


@app.get(
        "/chats/doctor/{doctor_id}",
         tags=["chat"], 
         response_model=list[Chat],
         summary='Возвращает список чатов врача')
async def get_list_chat_for_doctor(
    doctor_id: uuid.UUID, 
    session: AsyncSession = Depends(database.get_async_session)
    ) -> list[Chat]:
    return await crud.get_list_chat(session, doctor_id=doctor_id)


@app.get(
        "/chats/patient/{patient_id}",
         tags=["chat"], 
         response_model=list[Chat],
         summary='Возвращает список чатов пациента')
async def get_list_chat_for_patient(
    patient_id: uuid.UUID, 
    session: AsyncSession = Depends(database.get_async_session)
    ) -> list[Chat]:
    return await crud.get_list_chat(session, patient_id=patient_id)


# @app.post("/messages", response_model=Message, tags=["message"])
# async def add_message(
#     message: MessageIn, 
#     session: AsyncSession = Depends(database.get_async_session)) -> Message:
#     created_message = await crud.create_message(session, message)
#     created_message.message = CIPHER_SUITE.decrypt(created_message.message).decode()
#     return created_message


# @app.get("/messages/{message_id}", response_model=Message, tags=["message"])
# async def get_message(
#     message_id: uuid.UUID, 
#     session: AsyncSession = Depends(database.get_async_session)) -> Message:
#     msg = await crud.get_message(session, message_id)
#     if msg is not None:
#         msg.message = CIPHER_SUITE.decrypt(msg.message).decode()
#         return msg
#     raise HTTPException(status_code=404, detail="Сообщение не найдено")


@app.get("/messages/last/{chat_id}", response_model=list[Message], tags=["message"])
async def get_last_messages(
    chat_id: int, 
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(database.get_async_session)) -> list[Message]:
    messages = await crud.get_last_messages(session, chat_id, skip, limit)
    for msg in messages:
        msg.message = CIPHER_SUITE.decrypt(msg.message).decode()
    return messages


# @app.put("/messages/{message_id}", response_model=Message, tags=['message'])
# async def update_message(
#     message_id: uuid.UUID,
#     message_update: MessageUpdate, 
#     session: AsyncSession = Depends(database.get_async_session)
#     ) -> Message:
#     message = await crud.update_message(session, message_id, message_update)
#     if message is not None:
#         return message
#     raise HTTPException(status_code=404, detail="Сообщение не найдено")


@app.delete("/messages/{message_id}", response_model=Message, tags=['message'])
async def delete_message(
    message_id: uuid.UUID,
    session: AsyncSession = Depends(database.get_async_session)
    ) -> Message:
    deleted_message = await crud.delete_message(session, message_id)
    if deleted_message is None:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    deleted_message.message = CIPHER_SUITE.decrypt(deleted_message.message).decode()
    return deleted_message


@app.post("/messages/files", tags=["message"])
async def add_files_to_storage(
    files: list[UploadFile] = File(...)
    ):
    path_and_name_saved_files = []
    for file in files:
        extension = EXTENSIONS.get(file.content_type)
        if extension:
            path_to_file = create_path_to_file(app_config.path_to_storage, file.filename)
            create_file(file, path_to_file)
            path_and_name_saved_files.append({'name': file.filename, 'path_to_file': path_to_file})
    return path_and_name_saved_files


# @app.delete("/messages/files/{file_id}", response_model=MessageDocument, tags=['message'])
# async def delete_file(
#     file_id: uuid.UUID,
#     session: AsyncSession = Depends(database.get_async_session)
#     ): 
#     deleted_file = await crud.delete_file(session, file_id)
#     if deleted_file is not None:
#         os.remove(deleted_file.path_to_file)
#         return deleted_file
#     raise HTTPException(status_code=404, detail="Документ не найден")


@app.post(
        '/meetings',
        summary="Добавляет идентификатор встречи в базу",
        tags=['meetings']
)
async def create_meeting(
    meeting: schemas.MeetingIn,
    session: AsyncSession = Depends(database.get_async_session)
):
    meeting_id = await get_meeting_id(**meeting.model_dump(exclude={'record_id'}))
    return await crud.create_meeting(session, meeting_id, meeting)


@app.get("/meetings/{meeting_id}", response_model=schemas.Meeting, tags=["meetings"])
async def get_meeting(
    meeting_id: int, 
    session: AsyncSession = Depends(database.get_async_session)
):
    meeting = await get_meeting_info(session, meeting_id)
    if meeting is not None:
        return meeting
    raise HTTPException(status_code=404, detail="Встреча не найдена")


@app.get("/meetings", response_model=list[schemas.MeetingDB], tags=["meetings"])
async def get_meetings( 
    session: AsyncSession = Depends(database.get_async_session)
):
    return await crud.get_meetings_list(session)


@app.on_event("startup")
async def on_startup():
    await database.DB_INITIALIZER.init_database(
        app_config.postgres_dsn_async.unicode_string()
    )


async def get_meeting_id(topic, start_date, start_time):
    access_token = get_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "topic": topic,
        'start_time': f'{start_date}T{start_time}:00',
        "type": 2,
        "timezone": 'Europe/Moscow',
        "settings": {
            "waiting_room": True,  
        }
    }
    resp = requests.post(f"{api_base_url}/users/me/meetings", 
                        headers=headers, 
                        json=payload)
    
    if resp.status_code != 201:
        raise HTTPException(status_code=500, detail="Не удается создать ссылку на собрание")
    response_data = resp.json()
    return response_data["id"]


async def get_meeting_info(session, meeting_id):
    if await crud.get_meeting(session, meeting_id) is None:
        return None

    access_token = get_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    resp = requests.get(f"{api_base_url}/meetings/{meeting_id}", 
                        headers=headers)

    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="Не удается получить информацию о встрече")
    response_data = resp.json()
    return response_data


def get_token():
    auth_header = generate_basic_auth_header(app_config.CLIENT_ID, app_config.CLIENT_SECRET.get_secret_value())
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_header}"
    }
    data = {
        "grant_type": "account_credentials",
        "account_id": app_config.ACCOUNT_ID,
    }
    response = requests.post(auth_token_url, 
                            headers=headers, 
                            data=data)
    
    if response.status_code!=200:
        raise HTTPException(status_code=500, detail="Не удается получить токен доступа")
    response_data = response.json()
    access_token = response_data["access_token"]
    return access_token


def generate_basic_auth_header(client_id, client_secret):
    auth_str = f"{client_id}:{client_secret}"
    base64_encoded_str = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    return base64_encoded_str


def create_path_to_file(path_to_storage: str, file_name: str):
    extension = pathlib.Path(file_name).suffix
    return os.path.join(path_to_storage, str(uuid.uuid4()) + extension)


def create_file(file: UploadFile, path_to_file: str):
    try:
        with open(path_to_file, 'wb') as out_file:
            out_file.write(file.file.read())
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка при работе с файлом")
    