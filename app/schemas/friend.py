from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from models.friend import FriendStatus

class FriendRequestBase(BaseModel):
    receiver_id: UUID

class FriendRequestCreate(FriendRequestBase):
    pass

class FriendRequestResponse(BaseModel):
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    status: FriendStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FriendRequestUpdate(BaseModel):
    status: FriendStatus