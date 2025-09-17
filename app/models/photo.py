from sqlalchemy import Column, String, DateTime, ForeignKey, func, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from core.database import Base

class Photo(Base):
    __tablename__ = "photos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    filename = Column(String(255), nullable=False)
    original_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500))
    description = Column(String(500))
    is_public = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    place = relationship("Place", back_populates="photos")
    user = relationship("User", backref="photos")
    
    def __repr__(self):
        return f"<Photo {self.filename}>"