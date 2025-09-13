from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class MessageBase(BaseModel):
    receiver_id: UUID
    content: str

class MessageCreate(MessageBase):
    pass

class MessageResponse(BaseModel):
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attribute = True