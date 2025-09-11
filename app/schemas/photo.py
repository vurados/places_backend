from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class PhotoBase(BaseModel):
    description: Optional[str] = None
    is_public: bool = True

class PhotoCreate(PhotoBase):
    pass

class PhotoResponse(PhotoBase):
    id: UUID
    place_id: UUID
    user_id: UUID
    filename: str
    original_url: str
    thumbnail_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True