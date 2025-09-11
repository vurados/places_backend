from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, func, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Route(Base):
    __tablename__ = "routes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    places_order = Column(ARRAY(UUID))  # ordered list of place IDs
    metadata = Column(JSONB)  # distance, estimated time, etc.
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", backref="created_routes")
    collections = relationship("CollectionRoute", back_populates="route")
    
    def __repr__(self):
        return f"<Route {self.name}>"