from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID
from datetime import datetime
from app.models.notification import NotificationType

class NotificationBase(BaseModel):
    type: NotificationType
    title: str
    message: str
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None
    metadata: Optional[dict] = None

class NotificationCreate(NotificationBase):
    user_id: UUID

class NotificationResponse(NotificationBase):
    id: UUID
    user_id: UUID
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True

class NotificationUpdate(BaseModel):
    is_read: bool