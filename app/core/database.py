from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import settings

# Определяем Base
Base = declarative_base()

# Используем property для получения DATABASE_URI
database_url = settings.DATABASE_URI

if not database_url:
    raise ValueError("DATABASE_URI is not set in the configuration.")

engine = create_async_engine(
    database_url,
    echo=False,
    future=True,
    poolclass=NullPool,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

__all__ = ["Base", "engine", "AsyncSessionLocal", "get_db"]