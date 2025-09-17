from sqlalchemy.ext.asyncio import AsyncSession  # Добавляем импорт
from sqlalchemy import select, func, or_
from typing import List, Optional
from uuid import UUID
from services.redis_service import redis_client

from models import User, Place

async def search_users(
    db: AsyncSession,
    query: str,
    skip: int = 0,
    limit: int = 50,
    current_user_id: Optional[UUID] = None
):
    # Проверяем кеш
    params = {"skip": skip, "limit": limit, "current_user_id": str(current_user_id) if current_user_id else None}
    cached = await redis_client.get_cached_search("users", query, params)
    if cached:
        return cached
    
    search_query = func.plainto_tsquery('russian', query)
    
    stmt = select(User).where(
        User.search_vector.op('@@')(search_query)
    ).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    # Если пользователь аутентифицирован, исключаем его из результатов
    if current_user_id:
        users = [user for user in users if user.id != current_user_id]
        
    await redis_client.set_cached_search("users", query, params, users)
    return users

async def search_places(
    db: AsyncSession,
    query: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: Optional[float] = None,
    skip: int = 0,
    limit: int = 50
):
    search_query = func.plainto_tsquery('russian', query)
    
    stmt = select(Place).where(
        Place.search_vector.op('@@')(search_query) &
        Place.is_public == True
    )
    
    # Если указаны координаты, добавляем фильтр по расстоянию
    if latitude and longitude and radius_km:
        # Преобразуем км в градусы (примерно 1km = 0.009 градусов)
        radius_deg = radius_km * 0.009
        stmt = stmt.where(
            (Place.latitude.between(latitude - radius_deg, latitude + radius_deg)) &
            (Place.longitude.between(longitude - radius_deg, longitude + radius_deg))
        )
    
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    places = result.scalars().all()
    return places

async def global_search(
    db: AsyncSession,
    query: str,
    current_user_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 50
):
    # Ищем пользователей
    users = await search_users(db, query, skip, limit, current_user_id)
    
    # Ищем места
    places = await search_places(db, query, skip=skip, limit=limit)
    
    return {
        "users": users,
        "places": places
    }