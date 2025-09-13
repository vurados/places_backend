from sqlalchemy import JSON, Column, String, Text, Boolean, DateTime, ForeignKey, func, ARRAY, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Place(Base):
    __tablename__ = "places"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    address = Column(String(500))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    type = Column(String(100))  # restaurant, park, museum, etc.
    tags = Column(ARRAY(String(100)))
    metadata_info = Column(JSONB().with_variant(JSON, 'sqlite'))  # additional flexible data
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # admin verified
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", backref="created_places")
    reviews = relationship("Review", back_populates="place", cascade="all, delete")
    photos = relationship("Photo", back_populates="place", cascade="all, delete")
    
    def __repr__(self):
        return f"<Place {self.name}>"