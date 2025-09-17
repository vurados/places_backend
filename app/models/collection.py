from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from core.database import Base

class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50), nullable=False)  # 'want_to_visit', 'visited', 'custom'
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="collections")
    routes = relationship("CollectionRoute", back_populates="collection")
    
    def __repr__(self):
        return f"<Collection {self.name}>"

class CollectionRoute(Base):
    __tablename__ = "collection_routes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collection_id = Column(UUID(as_uuid=True), ForeignKey("collections.id"), nullable=False)
    route_id = Column(UUID(as_uuid=True), ForeignKey("routes.id"), nullable=False)
    
    added_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    collection = relationship("Collection", back_populates="routes")
    route = relationship("Route", back_populates="collections")
    
    def __repr__(self):
        return f"<CollectionRoute {self.collection_id} - {self.route_id}>"