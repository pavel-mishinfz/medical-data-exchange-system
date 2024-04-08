import uuid
from sqlalchemy import Column, Integer, UUID, Text, TIMESTAMP, func

from .database import Base


class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(UUID(as_uuid=True), nullable=False)
    patient_id = Column(UUID(as_uuid=True), nullable=False)


class Message(Base):
    __tablename__ = "message"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    message = Column(Text, nullable=False)
    sender_id = Column(UUID(as_uuid=True), nullable=False)
    chat_id = Column(Integer, nullable=False)
    send_date = Column(TIMESTAMP, default=func.now())
    update_date = Column(TIMESTAMP, default=None, onupdate=func.now())
