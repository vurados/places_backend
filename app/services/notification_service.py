from sqlalchemy.ext.asyncio import AsyncSession
from models.notification import Notification, NotificationType
from schemas.notification import NotificationCreate
from typing import Optional
from uuid import UUID

async def create_notification(
    db: AsyncSession,
    notification_data: NotificationCreate
):
    db_notification = Notification(**notification_data.dict())
    db.add(db_notification)
    await db.commit()
    await db.refresh(db_notification)
    return db_notification

async def get_user_notifications(
    db: AsyncSession,
    user_id: UUID,
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False
):
    from sqlalchemy import select
    query = select(Notification).where(Notification.user_id == user_id)
    
    if unread_only:
        query = query.where(Notification.is_read == False)
    
    query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    notifications = result.scalars().all()
    return notifications

async def mark_notification_as_read(
    db: AsyncSession,
    notification_id: UUID,
    user_id: UUID
):
    from sqlalchemy import select
    result = await db.execute(
        select(Notification).where(
            (Notification.id == notification_id) &
            (Notification.user_id == user_id)
        )
    )
    notification = result.scalars().first()
    
    if notification:
        notification.is_read = True
        await db.commit()
        await db.refresh(notification)
    
    return notification

async def mark_all_notifications_as_read(
    db: AsyncSession,
    user_id: UUID
):
    from sqlalchemy import update
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id)
        .values(is_read=True)
    )
    await db.commit()