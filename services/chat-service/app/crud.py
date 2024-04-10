import uuid
from .database import models
from .schemas import ChatIn, MessageIn, MessageUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, update, delete


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


async def create_message(session: AsyncSession, message_in: MessageIn) -> models.Message | None:
    """
    Создает сообщение
    """

    db_message = models.Message(
        sender_id=message_in.sender_id,
        chat_id=message_in.chat_id,
        message=message_in.message
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
        .filter(models.Message.chat_id == chat_id)  
        .order_by(models.Message.send_date.asc())
        .offset(skip)  
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def update_message(
        session: AsyncSession, 
        message_id: uuid.UUID,
        message: MessageUpdate) -> models.Message | None:
    """
    Обновляет сообщение
    """ 
    result = await session.execute(update(models.Message) \
                                   .where(models.Message.id == message_id) \
                                   .values(message.model_dump())
                                   )
    await session.commit()
    if result:
        return await get_message(session, message_id)
    return None


async def delete_message(
        session: AsyncSession, message_id: uuid.UUID
    ) -> models.Message | None:
    """
    Удаляет информацию о сообщение
    """

    deleted_message = await get_message(session, message_id)
    if deleted_message is None:
        return None

    await session.delete(deleted_message)
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


async def get_file(
        session: AsyncSession, 
        file_id: uuid.UUID) -> models.MessageDocument | None:
    """
    Возвращает информацию о пложении
    """ 
    
    result = await session.execute(select(models.MessageDocument) \
                                   .filter(models.MessageDocument.id == file_id) \
                                   .limit(1)
                                   )
    return result.scalars().one_or_none()


async def delete_file(
        session: AsyncSession, file_id: uuid.UUID
    ) -> models.MessageDocument | None:
    """
    Удаляет информацию о вложении
    """

    deleted_file = await get_file(session, file_id)
    await session.execute(delete(models.MessageDocument) \
                          .filter(models.MessageDocument.id == file_id)
                          )
    await session.commit()
    return deleted_file


async def get_list_chat(
        session: AsyncSession, 
        doctor_id: uuid.UUID | None = None, 
        patient_id: uuid.UUID | None = None) -> list[models.Chat]:
    """
    Возвращает список чатов врача или пациента
    """ 
    
    stmt = (
        select(models.Chat)
        .filter(
            or_(
                models.Chat.doctor_id == doctor_id,
                models.Chat.patient_id == patient_id)
                )  
    )
    result = await session.execute(stmt)
    return result.scalars().all()

