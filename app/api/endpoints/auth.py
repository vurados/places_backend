from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timedelta, timezone
import uuid

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, UserLogin, UserOAuthCreate
from app.services.auth_service import (
    authenticate_user, 
    authenticate_user_by_username,
    create_access_token,
    hash_password,
    generate_salt
)
from app.services.email_service import send_verification_email

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # Проверяем, что email или username не заняты
    if user_data.email:
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    if user_data.username:
        result = await db.execute(select(User).where(User.username == user_data.username))
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Генерируем соль и хешируем пароль
    salt = generate_salt()
    password_hash = hash_password(user_data.password, salt)
    
    # Создаем пользователя
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password_hash=password_hash,
        password_salt=salt,
        is_verified=False  # Требует верификации по email
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Отправляем email для верификации (в фоне)
    if user_data.email:
        background_tasks.add_task(send_verification_email, db_user.email, db_user.id)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(
    form_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    # Определяем, это email или username
    if "@" in form_data.login:
        user = await authenticate_user(db, form_data.login, form_data.password)
    else:
        user = await authenticate_user_by_username(db, form_data.login, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated",
        )
    
    # Обновляем время последнего входа
    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    
    # Создаем токены
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=timedelta(days=30)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@router.post("/oauth")
async def oauth_login(
    oauth_data: UserOAuthCreate,
    db: AsyncSession = Depends(get_db)
):
    # Ищем пользователя по provider_id
    result = await db.execute(
        select(User).where(
            User.oauth_data["providers"].astext.contains(f'"{oauth_data.provider}"')
        )
    )
    user = result.scalars().first()
    
    if user:
        # Обновляем данные пользователя
        user.last_login = datetime.now(timezone.utc)
        await db.commit()
    else:
        # Создаем нового пользователя через OAuth
        db_user = User(
            email=oauth_data.email,
            first_name=oauth_data.first_name,
            last_name=oauth_data.last_name,
            username=oauth_data.username,
            avatar_url=oauth_data.avatar_url,
            is_verified=True,  # OAuth пользователи считаются верифицированными
            oauth_providers=[oauth_data.provider],
            oauth_data={
                oauth_data.provider: {
                    "id": oauth_data.provider_id,
                    "access_token": oauth_data.access_token
                }
            }
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        user = db_user
    
    # Создаем токены
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=timedelta(days=30)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }