from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Reaction(Base):
    __tablename__ = "reactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    type = Column(String(50), nullable=False)  # like, love, wow, etc.
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    review = relationship("Review", back_populates="reactions")
    user = relationship("User", backref="reactions")
    
    def __repr__(self):
        return f"<Reaction {self.type} by User {self.user_id}>"