from sqlalchemy import Column, Text, Integer, DateTime, ForeignKey, func, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from core.database import Base

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text)
    is_public = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    place = relationship("Place", back_populates="reviews")
    user = relationship("User", backref="reviews")
    reactions = relationship("Reaction", back_populates="review", cascade="all, delete")
    
    def __repr__(self):
        return f"<Review for Place {self.place_id} by User {self.user_id}>"