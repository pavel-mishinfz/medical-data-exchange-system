import uuid
import datetime
import base64
from cryptography.fernet import Fernet

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, update, delete

from .database import models
from .schemas import ChatIn, MessageIn, MessageUpdate, MeetingIn
from . import config


cfg: config.Config = config.load_config();
CIPHER_SUITE: Fernet = Fernet(
    base64.b64decode(cfg.encrypt_key.get_secret_value())
)


async def create_chat(session: AsyncSession, chat_in: ChatIn) -> models.Chat:
    """
    Создает новый чат
    """

    db_chat = models.Chat(
        doctor_id=chat_in.doctor_id,
        patient_id=chat_in.patient_id,
    )

    session.add(db_chat)
    await session.commit()
    await session.refresh(db_chat)
    return db_chat


async def get_list_chat(
        session: AsyncSession, 
        user_id: uuid.UUID) -> list[models.Chat]:
    """
    Возвращает список чатов врача или пациента
    """ 
    
    stmt = (
        select(models.Chat)
        .filter(
            or_(
                models.Chat.doctor_id == user_id,
                models.Chat.patient_id == user_id
            )
        )  
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_message(session: AsyncSession, message_in: MessageIn) -> models.Message | None:
    """
    Создает сообщение
    """

    db_message = models.Message(
        sender_id=message_in.sender_id,
        chat_id=message_in.chat_id,
        message=CIPHER_SUITE.encrypt(message_in.message.encode())
    )

    session.add(db_message)
    await session.commit()
    await session.refresh(db_message)
    return db_message


async def get_message(
        session: AsyncSession, 
        message_id: uuid.UUID) -> models.Message | None:
    """
    Возвращает информацию о сообщении
    """ 
    
    result = await session.execute(select(models.Message) \
                                   .filter(models.Message.id == message_id) \
                                   .limit(1)
                                   )
    return result.scalars().one_or_none()


async def get_last_messages(
        session: AsyncSession, 
        chat_id: int, 
        skip: int, 
        limit: int) -> list[models.Message]:
    """
    Возвращает список последних сообщений
    """ 
    
    stmt = (
        select(models.Message)
        .filter(models.Message.chat_id == chat_id, models.Message.is_deleted == False)
        .order_by(models.Message.send_date.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


# async def update_message(
#         session: AsyncSession, 
#         message_id: uuid.UUID,
#         message: MessageUpdate) -> models.Message | None:
#     """
#     Обновляет сообщение
#     """ 
#     result = await session.execute(update(models.Message) \
#                                    .where(models.Message.id == message_id) \
#                                    .values(message.model_dump())
#                                    )
#     await session.commit()
#     if result:
#         return await get_message(session, message_id)
#     return None


async def delete_message(
        session: AsyncSession, message_id: uuid.UUID
    ) -> models.Message | None:
    """
    Удаляет информацию о сообщение
    """

    deleted_message = await get_message(session, message_id)
    if deleted_message is None:
        return None

    deleted_message.is_deleted = True
    for document in deleted_message.documents:
        document.is_deleted = True
    await session.commit()

    return deleted_message


async def create_file(
    session: AsyncSession, message_id: uuid.UUID, file_name: str, path_to_file: str
    ) -> models.MessageDocument:
    """
    Создает файл сообщения
    """
    db_file = models.MessageDocument(
        name=file_name,
        path_to_file=path_to_file,
        id_message=message_id
    )

    session.add(db_file)
    await session.commit()
    await session.refresh(db_file)
    return db_file


# async def get_file(
#         session: AsyncSession, 
#         file_id: uuid.UUID) -> models.MessageDocument | None:
#     """
#     Возвращает информацию о пложении
#     """ 
    
#     result = await session.execute(select(models.MessageDocument) \
#                                    .filter(models.MessageDocument.id == file_id) \
#                                    .limit(1)
#                                    )
#     return result.scalars().one_or_none()


# async def delete_file(
#         session: AsyncSession, file_id: uuid.UUID
#     ) -> models.MessageDocument | None:
#     """
#     Удаляет информацию о вложении
#     """

#     deleted_file = await get_file(session, file_id)
#     await session.execute(delete(models.MessageDocument) \
#                           .filter(models.MessageDocument.id == file_id)
#                           )
#     await session.commit()
#     return deleted_file


async def create_meeting(session: AsyncSession, meeting_id: int, meeting: MeetingIn) -> models.Meeting:
    """
    Создает новую встречу
    """

    db_meeting = models.Meeting(
        meeting_id=meeting_id,
        record_id=meeting.record_id,
        start_date=meeting.start_date,
        start_time=meeting.start_time
    )

    session.add(db_meeting)
    await session.commit()
    await session.refresh(db_meeting)
    return db_meeting


async def get_meeting(
        session: AsyncSession, 
        meeting_id: uuid.UUID) -> models.Meeting | None:
    """
    Возвращает информацию о встрече
    """ 
    
    result = await session.execute(select(models.Meeting) \
                                   .filter(models.Meeting.meeting_id == meeting_id) \
                                   .limit(1)
                                   )
    return result.scalars().one_or_none()


async def get_meetings_list(
        session: AsyncSession
    ) -> list[models.Meeting]:
    """
    Возвращает список встреч
    """ 
    
    result = await session.execute(select(models.Meeting)
                                   .filter(models.Meeting.start_date >= datetime.datetime.today().date())
                                   )
    return result.scalars().all()