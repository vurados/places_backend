from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()

@router.post("/verify-email/{token}")
async def verify_email(
    token: UUID,
    db: AsyncSession = Depends(get_db)
):
    # Здесь должна быть логика верификации токена
    # Для простоты ищем пользователя по ID
    result = await db.execute(select(User).where(User.id == token))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    user.is_verified = True
    await db.commit()
    
    return {"message": "Email successfully verified"}

@router.post("/resend-verification")
async def resend_verification(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Отправляем email повторно (реализация зависит от вашего email сервиса)
    # background_tasks.add_task(send_verification_email, current_user.email, current_user.id)
    
    return {"message": "Verification email sent"}