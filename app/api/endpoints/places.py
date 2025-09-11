from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.models.place import Place
from app.models.photo import Photo
from app.schemas.place import PlaceCreate, PlaceResponse, PlaceUpdate
from app.schemas.photo import PhotoResponse
from app.services.auth_service import get_current_user
from app.services.image_service import process_and_upload_image

router = APIRouter()

@router.get("/", response_model=List[PlaceResponse])
async def get_places(
    skip: int = 0,
    limit: int = 100,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    # TODO: Implement location-based filtering
    # For now, return all public places
    from sqlalchemy import select
    result = await db.execute(select(Place).where(Place.is_public == True).offset(skip).limit(limit))
    places = result.scalars().all()
    return places

@router.post("/", response_model=PlaceResponse)
async def create_place(
    place_data: PlaceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_place = Place(**place_data.dict(), created_by=current_user.id)
    db.add(db_place)
    await db.commit()
    await db.refresh(db_place)
    return db_place

@router.post("/{place_id}/photos", response_model=PhotoResponse)
async def upload_place_photo(
    place_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if place exists and user has access
    from sqlalchemy import select
    result = await db.execute(select(Place).where(Place.id == place_id))
    place = result.scalars().first()
    
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    
    if place.created_by != current_user.id and not place.is_public:
        raise HTTPException(status_code=403, detail="Not authorized to add photos to this place")
    
    # Process and upload image
    image_data = await process_and_upload_image(file, str(current_user.id))
    
    # Create photo record
    db_photo = Photo(
        place_id=place_id,
        user_id=current_user.id,
        filename=image_data["original_filename"],
        original_url=image_data["original_url"],
        thumbnail_url=image_data["thumbnail_url"]
    )
    
    db.add(db_photo)
    await db.commit()
    await db.refresh(db_photo)
    return db_photo

@router.get("/{place_id}", response_model=PlaceResponse)
async def get_place(
    place_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select
    result = await db.execute(select(Place).where(Place.id == place_id))
    place = result.scalars().first()
    
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    
    if not place.is_public:
        # TODO: Check if user has access to private places
        raise HTTPException(status_code=403, detail="Not authorized to access this place")
    
    return place