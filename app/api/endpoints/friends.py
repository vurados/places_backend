from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from core.database import get_db
from models.notification import NotificationType
from models.user import User
from models.friend import FriendRequest, FriendStatus
from schemas.notification import NotificationCreate
from schemas.user import UserResponse
from schemas.friend import FriendRequestCreate, FriendRequestResponse, FriendRequestUpdate
from services.auth_service import get_current_user
from services.notification_service import create_notification

router = APIRouter()

@router.get("/requests", response_model=List[FriendRequestResponse])
async def get_friend_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from sqlalchemy import select
    result = await db.execute(
        select(FriendRequest).where(
            (FriendRequest.receiver_id == current_user.id) & 
            (FriendRequest.status == FriendStatus.PENDING)
        )
    )
    requests = result.scalars().all()
    return requests

@router.post("/requests", response_model=FriendRequestResponse)
async def send_friend_request(
    request_data: FriendRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if receiver exists
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == request_data.receiver_id))
    receiver = result.scalars().first()
    
    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if request already exists
    result = await db.execute(
        select(FriendRequest).where(
            (FriendRequest.sender_id == current_user.id) & 
            (FriendRequest.receiver_id == request_data.receiver_id)
        )
    )
    existing_request = result.scalars().first()
    
    if existing_request:
        raise HTTPException(status_code=400, detail="Friend request already sent")
    
    # Create new request
    db_request = FriendRequest(
        sender_id=current_user.id,
        receiver_id=request_data.receiver_id
    )
    db.add(db_request)
    await db.commit()
    await db.refresh(db_request)

    notification_data = NotificationCreate(
        user_id=request_data.receiver_id,
        type=NotificationType.FRIEND_REQUEST,
        title="Новый запрос в друзья",
        message=f"Пользователь {current_user.first_name} {current_user.last_name} отправил вам запрос в друзья",
        related_entity_type="user",
        related_entity_id=current_user.id,
        metadata={"request_id": str(db_request.id)}
    )
    await create_notification(db, notification_data)

    return db_request

@router.patch("/requests/{request_id}", response_model=FriendRequestResponse)
async def update_friend_request(
    request_id: UUID,
    request_data: FriendRequestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from sqlalchemy import select
    result = await db.execute(
        select(FriendRequest).where(
            (FriendRequest.id == request_id) & 
            (FriendRequest.receiver_id == current_user.id)
        )
    )
    friend_request = result.scalars().first()
    
    if not friend_request:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    friend_request.status = request_data.status
    await db.commit()
    await db.refresh(friend_request)

    if request_data.status == FriendStatus.ACCEPTED:
        # Создаем уведомление для отправителя
        notification_data = NotificationCreate(
            user_id=friend_request.sender_id,
            type=NotificationType.FRIEND_ACCEPTED,
            title="Запрос в друзья принят",
            message=f"Пользователь {current_user.first_name} {current_user.last_name} принял ваш запрос в друзья",
            related_entity_type="user",
            related_entity_id=current_user.id
        )
        await create_notification(db, notification_data)

    return friend_request

@router.get("/friends", response_model=List[UserResponse])
async def get_friends(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from sqlalchemy import select, or_
    # Get all accepted friend requests where current user is either sender or receiver
    result = await db.execute(
        select(FriendRequest).where(
            (FriendRequest.status == FriendStatus.ACCEPTED) &
            (
                (FriendRequest.sender_id == current_user.id) |
                (FriendRequest.receiver_id == current_user.id)
            )
        )
    )
    friend_requests = result.scalars().all()
    
    friend_ids = []
    for req in friend_requests:
        if req.sender_id == current_user.id:
            friend_ids.append(req.receiver_id)
        else:
            friend_ids.append(req.sender_id)
    
    # Get user objects for friend IDs
    if not friend_ids:
        return []
    
    result = await db.execute(select(User).where(User.id.in_(friend_ids)))
    friends = result.scalars().all()
    return friends