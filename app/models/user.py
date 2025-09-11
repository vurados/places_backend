from sqlalchemy import Column, String, Boolean, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=True)  # Может быть null для OAuth
    phone = Column(String(20), unique=True, nullable=True)   # Может быть null для OAuth
    
    # Поля для локальной аутентификации
    password_hash = Column(String(255), nullable=True)      # Может быть null для OAuth
    password_salt = Column(String(255), nullable=True)      # Соль для пароля
    
    # OAuth провайдеры
    oauth_providers = Column(JSONB, default=[])  # Список подключенных OAuth провайдеров
    oauth_data = Column(JSONB, default={})       # Данные OAuth (id, tokens, etc.)
    
    # Основная информация
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    username = Column(String(50), unique=True, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Статусы
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Временные метки
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # GDPR compliance
    data_processing_consent = Column(Boolean, default=False)
    privacy_policy_accepted = Column(Boolean, default=False)
    marketing_consent = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<User {self.email or self.username}>"