import os
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus

load_dotenv()

class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "Urban Places Social App"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change_this_in_production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_USER: str = os.getenv("DB_USER", "test_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "test_password")
    DB_NAME: str = os.getenv("DB_NAME", "test_db")
    
    # Убираем DATABASE_URI из полей, будем вычислять его динамически
    # через property чтобы избежать проблем с валидацией
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    
    # MinIO
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ROOT_USER: str = os.getenv("MINIO_ROOT_USER", "minioadmin")
    MINIO_ROOT_PASSWORD: str = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
    MINIO_BUCKET: str = os.getenv("MINIO_BUCKET", "places-social")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "False").lower() == "true"
    
    # Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    # Динамическое свойство для DATABASE_URI
    @property
    def DATABASE_URI(self) -> str:
        """Динамически генерируем DATABASE_URI"""
        user_escaped = quote_plus(self.DB_USER)
        password_escaped = quote_plus(self.DB_PASSWORD) if self.DB_PASSWORD else ""
        
        if password_escaped:
            return f"postgresql+asyncpg://{user_escaped}:{password_escaped}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            return f"postgresql+asyncpg://{user_escaped}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore"  # Игнорируем дополнительные поля
    )

settings = Settings()