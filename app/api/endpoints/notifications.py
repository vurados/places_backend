from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse, NotificationUpdate
from app.services.auth_service import get_current_user
from app.services.notification_service import (
    get_user_notifications,
    mark_notification_as_read,
    mark_all_notifications_as_read
)

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = await get_user_notifications(
        db, current_user.id, skip, limit, unread_only
    )
    return notifications

@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = await mark_notification_as_read(db, notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "notification marked as read"}

@router.post("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await mark_all_notifications_as_read(db, current_user.id)
    return {"status": "all notifications marked as read"}

@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from sqlalchemy import select, func
    result = await db.execute(
        select(func.count(Notification.id)).where(
            (Notification.user_id == current_user.id) &
            (Notification.is_read == False)
        )
    )
    count = result.scalar()
    return {"unread_count": count}