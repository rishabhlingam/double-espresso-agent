from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

# MESSAGE SCHEMAS
class MessageBase(BaseModel):
    role: str
    content: str


class MessageCreate(MessageBase):
    content: str
    role: str = "user"


class MessageRead(MessageBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# CHAT SCHEMAS
class ChatBase(BaseModel):
    type: str
    parent_chat_id: Optional[int] = None
    parent_message_id: Optional[int] = None


class ChatCreate(ChatBase):
    pass


class ChatRead(ChatBase):
    id: int
    messages: List[MessageRead] = []

    model_config = ConfigDict(from_attributes=True)

# FORK REQUEST SCHEMA
class ForkRequest(BaseModel):
    parent_chat_id: int
    parent_message_id: int
