import uuid
from sqlalchemy import Column, Integer, String, UUID, Text, TIMESTAMP, ForeignKey, func, BigInteger, Date, CHAR, Boolean, LargeBinary
from sqlalchemy.orm import mapped_column, relationship

from .database import Base


class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(UUID(as_uuid=True), nullable=False)
    patient_id = Column(UUID(as_uuid=True), nullable=False)


class Message(Base):
    __tablename__ = "message"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    message = Column(LargeBinary)
    sender_id = Column(UUID(as_uuid=True), nullable=False)
    chat_id = Column(Integer, nullable=False)
    send_date = Column(TIMESTAMP, default=func.now())
    documents = relationship('MessageDocument', backref='msg', lazy="selectin")
    is_deleted = Column(Boolean, default=False)


class MessageDocument(Base):
    __tablename__ = "message_document"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    path_to_file = Column(String, nullable=False)
    id_message = mapped_column(ForeignKey('message.id'), nullable=False)
    is_deleted = Column(Boolean, default=False)


class Meeting(Base):
    __tablename__ = "meeting"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    meeting_id = Column(BigInteger, nullable=False)
    record_id = Column(UUID(as_uuid=True), nullable=False)
    start_date = Column(Date, nullable=False)
    start_time = Column(CHAR(length=5), nullable=False)
