import uuid
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import Chat, ChatIn, Message, MessageIn, MessageUpdate
from . import crud
from . import config
from . import database

from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware


app_config: config.Config = config.load_config()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешите запросы с любых источников
    allow_credentials=True,
    allow_methods=["*"],  # Разрешите все HTTP-методы
    allow_headers=["*"],  # Разрешите все заголовки
)

room_managers = {}


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, msg: MessageIn):
        await self.add_messages_to_database(msg)
        for connection in self.active_connections:
            await connection.send_text(msg.message)

    @staticmethod
    async def add_messages_to_database(message: MessageIn):
        async for async_session in database.get_async_session():
            await crud.create_message(async_session, message)


@app.websocket("/ws/{chat_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int, client_id: uuid.UUID):
    if chat_id not in room_managers:
        room_managers[chat_id] = ConnectionManager()

    manager = room_managers[chat_id]

    await manager.connect(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            await manager.broadcast(MessageIn(message=msg, chat_id=chat_id, sender_id=client_id))
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        
templates = Jinja2Templates(directory="app/templates")
@app.get("/chat", tags=["chat"])
def get_chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


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


@app.post("/messages", response_model=Message, tags=["message"])
async def add_message(
    message: MessageIn, 
    session: AsyncSession = Depends(database.get_async_session)) -> Message:
    return await crud.create_message(session, message)


@app.get("/messages/{message_id}", response_model=Message, tags=["message"])
async def get_message(
    message_id: uuid.UUID, 
    session: AsyncSession = Depends(database.get_async_session)) -> Message:
    msg = await crud.get_message(session, message_id)
    if msg is not None:
        return msg
    raise HTTPException(status_code=404, detail="Сообщение не найдено")


@app.get("/last_messages/{chat_id}", response_model=list[Message], tags=["message"])
async def get_last_messages(
    chat_id: int, 
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(database.get_async_session)) -> list[Message]:
    return await crud.get_last_messages(session, chat_id, skip, limit)


@app.put("/messages/{message_id}", response_model=Message, tags=['message'])
async def update_message(
    message_id: uuid.UUID,
    message_update: MessageUpdate, 
    session: AsyncSession = Depends(database.get_async_session)
    ) -> Message:
    message = await crud.update_message(session, message_id, message_update)
    if message is not None:
        return message
    raise HTTPException(status_code=404, detail="Сообщение не найдено")


@app.delete("/messages/{message_id}", response_model=Message, tags=['message'])
async def delete_message(
    message_id: uuid.UUID,
    session: AsyncSession = Depends(database.get_async_session)
    ) -> Message:
    message = await crud.get_message(session, message_id)
    if await crud.delete_message(session, message_id):
        return message
    raise HTTPException(status_code=404, detail="Сообщение не найдено")


@app.on_event("startup")
async def on_startup():

    await database.DB_INITIALIZER.init_database(
        app_config.postgres_dsn_async.unicode_string()
        )
    