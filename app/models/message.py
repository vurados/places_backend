from sqlalchemy import Column, Text, DateTime, ForeignKey, func, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from core.database import Base

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_messages")
    
    def __repr__(self):
        return f"<Message from {self.sender_id} to {self.receiver_id}>"