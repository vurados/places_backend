from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from core.database import get_db
from models.notification import NotificationType
from models.user import User
from models.message import Message
from schemas.message import MessageCreate, MessageResponse
from schemas.notification import NotificationCreate
from services.auth_service import get_current_user
from services.notification_service import create_notification

router = APIRouter()

@router.get("/{user_id}", response_model=List[MessageResponse])
async def get_messages(
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user exists
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get messages between current user and the other user
    result = await db.execute(
        select(Message).where(
            (
                (Message.sender_id == current_user.id) & 
                (Message.receiver_id == user_id)
            ) | (
                (Message.sender_id == user_id) & 
                (Message.receiver_id == current_user.id)
            )
        ).order_by(Message.created_at.desc()).offset(skip).limit(limit)
    )
    messages = result.scalars().all()
    return messages

@router.post("/{user_id}", response_model=MessageResponse)
async def send_message(
    user_id: UUID,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if receiver exists
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id))
    receiver = result.scalars().first()
    
    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if users are friends (optional, depending on requirements)
    # For now, we allow sending messages to any user
    
    db_message = Message(
        sender_id=current_user.id,
        receiver_id=user_id,
        content=message_data.content
    )
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)

    notification_data = NotificationCreate(
        user_id=user_id,
        type=NotificationType.NEW_MESSAGE,
        title="Новое сообщение",
        message=f"У вас новое сообщение от {current_user.first_name} {current_user.last_name}",
        related_entity_type="message",
        related_entity_id=db_message.id,
        metadata={"preview": message_data.content[:100]}  # Первые 100 символов
    )
    await create_notification(db, notification_data)

    return db_message

@router.patch("/{message_id}/read")
async def mark_message_as_read(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from sqlalchemy import select
    result = await db.execute(
        select(Message).where(
            (Message.id == message_id) & 
            (Message.receiver_id == current_user.id)
        )
    )
    message = result.scalars().first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.is_read = True
    await db.commit()
    return {"status": "message marked as read"}