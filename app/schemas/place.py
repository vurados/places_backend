from pydantic import BaseModel, validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class PlaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: float
    longitude: float
    type: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: bool = True

class PlaceCreate(PlaceBase):
    pass

class PlaceUpdate(PlaceBase):
    pass

class PlaceResponse(PlaceBase):
    id: UUID
    created_by: UUID
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attribute = True