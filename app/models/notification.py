from sqlalchemy import JSON, Column, String, DateTime, ForeignKey, func, Boolean, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from core.database import Base
import enum

class NotificationType(enum.Enum):
    FRIEND_REQUEST = "friend_request"
    FRIEND_ACCEPTED = "friend_accepted"
    NEW_MESSAGE = "new_message"
    NEW_REACTION = "new_reaction"
    NEW_COMMENT = "new_comment"
    SYSTEM = "system"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    related_entity_type = Column(String(50))  # user, place, review, message, etc.
    related_entity_id = Column(UUID(as_uuid=True))
    metadata_info = Column(JSONB().with_variant(JSON, 'sqlite'))  # additional data
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="notifications")
    
    def __repr__(self):
        return f"<Notification {self.type} for User {self.user_id}>"