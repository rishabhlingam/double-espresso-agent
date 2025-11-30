from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Enum,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import Base

# Chat Type Enum
class ChatType(str, enum.Enum):
    primary = "primary"
    secondary = "secondary"

# Chat Model
class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)

    type = Column(Enum(ChatType), nullable=False, default=ChatType.primary)

    # For secondary chats
    parent_chat_id = Column(Integer, ForeignKey("chats.id"), nullable=True)
    parent_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)

    # ADK session ID associated with the chat
    adk_session_id = Column(String, nullable=False)

    title = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    messages = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="Message.id",
        foreign_keys="Message.chat_id"
    )

    # Link back to parent chat (for secondary chats)
    parent_chat = relationship(
        "Chat",
        remote_side=[id],
        uselist=False
    )

    # Message that created the secondary chat
    parent_message = relationship(
        "Message",
        uselist=False,
        foreign_keys=[parent_message_id]
    )


    # Only one secondary chat is allowed per parent message
    __table_args__ = (
        UniqueConstraint(
            "parent_message_id",
            name="uq_parent_message_secondary",
        ),
    )


# Message Model
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)

    role = Column(String, nullable=False)  # "user" | "assistant" | "system"
    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to Chat
    chat = relationship(
        "Chat",
        back_populates="messages",
        foreign_keys=[chat_id]
    )
