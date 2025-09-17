from sqlalchemy import Column, String, DateTime, ForeignKey, func, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from core.database import Base
import enum

class FriendStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    BLOCKED = "blocked"

class FriendRequest(Base):
    __tablename__ = "friend_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(FriendStatus), default=FriendStatus.PENDING)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_requests")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_requests")
    
    def __repr__(self):
        return f"<FriendRequest {self.sender_id} -> {self.receiver_id}: {self.status}>"