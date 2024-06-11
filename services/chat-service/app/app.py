import base64
import json
import os
import pathlib
import uuid
import requests
import aiofiles
from cryptography.fernet import Fernet

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import Chat, ChatIn, Message, MessageIn, MessageUpdate, MessageDocument
from . import schemas
from . import crud
from . import config
from . import database

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

    async def broadcast(self, message_in: MessageIn, files: list | None):
        message = await self.add_messages_to_database(message_in)
        path_and_name_saved_files = []
        if files:
            path_and_name_saved_files = await add_files_to_storage(message.chat_id, files)
        for file in path_and_name_saved_files:
            await self.add_files_to_database(message.id, file)
        data = {
            'id': str(message.id),
            'sender_id': str(message.sender_id),
            'send_date': message.send_date.isoformat(),
            'message': message.message,
            'documents': path_and_name_saved_files
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
        

@app.post(
        "/chats",
        tags=["chat"], 
        response_model=Chat,
        summary='Создает чат')
async def add_chat(chat: ChatIn, session: AsyncSession = Depends(database.get_async_session)) -> Chat:
    created_chat = await crud.create_chat(session, chat)
    chat_directory = os.path.join(ROOT_SERVICE_DIR, str(created_chat.id))
    os.makedirs(chat_directory)
    return created_chat


@app.get(
        "/chats/{user_id}",
         tags=["chat"], 
         response_model=list[Chat],
         summary='Возвращает список чатов пользователя')
async def get_list_chat_for_doctor(
    user_id: uuid.UUID, 
    session: AsyncSession = Depends(database.get_async_session)
    ) -> list[Chat]:
    return await crud.get_list_chat(session, user_id)


@app.get(
    "/chat_storage/{chat_id}/{file_name}",
    summary="Возвращает изображение пользователя",
    tags=["users"])
async def serve_chat_static_file(chat_id: int, file_name: str):
    chat_storage = os.path.join(ROOT_SERVICE_DIR, "chat_storage", str(chat_id))
    file_path = os.path.join(chat_storage, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(file_path)


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


async def add_files_to_storage(chat_id: int, files: list):
    path_and_name_saved_files = []
    for file_data in files:
        extension = EXTENSIONS.get(file_data['mime_type'])
        if extension:
            path_to_file = await create_path_to_file(app_config.path_to_storage, str(chat_id), file_data['file_name'])
            file_content = base64.b64decode(file_data['file_content'])
            await create_file(file_content, path_to_file)
            path_and_name_saved_files.append({'name': file_data['file_name'], 'path_to_file': path_to_file})
    return path_and_name_saved_files


async def create_path_to_file(path_to_storage: str, dir_name: str, file_name: str):
    extension = pathlib.Path(file_name).suffix
    path_to_storage = path_to_storage.split('/')[0]
    return os.path.join(path_to_storage, dir_name, str(uuid.uuid4()) + extension)


async def create_file(file_content: bytes, path_to_file: str):
    try:
        async with aiofiles.open(path_to_file, 'wb') as out_file:
            await out_file.write(file_content)
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка при работе с файлом")
    