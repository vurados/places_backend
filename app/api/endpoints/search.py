from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID

from core.database import get_db
from models.user import User
from models.place import Place
from schemas.user import UserResponse
from schemas.place import PlaceResponse
from services.auth_service import get_current_user
from services.search_service import search_users, search_places, global_search

router = APIRouter()

@router.get("/global")
async def search_global(
    q: str,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not q or len(q) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters long"
        )
    
    current_user_id = current_user.id if current_user else None
    results = await global_search(db, q, current_user_id, skip, limit)
    return results

@router.get("/users", response_model=List[UserResponse])
async def search_users_endpoint(
    q: str,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not q or len(q) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters long"
        )
    
    current_user_id = current_user.id if current_user else None
    users = await search_users(db, q, skip, limit, current_user_id)
    return users

@router.get("/places", response_model=List[PlaceResponse])
async def search_places_endpoint(
    q: str,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_km: Optional[float] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    if not q or len(q) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters long"
        )
    
    places = await search_places(db, q, lat, lng, radius_km, skip, limit)
    return places