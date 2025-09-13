import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Устанавливаем флаг тестирования
os.environ["TESTING"] = "True"

# Устанавливаем переменные окружения
os.environ.update({
    "DB_HOST": "postgres",
    "DB_PORT": "5432",
    "DB_USER": "test_user",
    "DB_PASSWORD": "test_password",
    "DB_NAME": "test_db",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "SECRET_KEY": "test_secret_key_for_tests"
})

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.core.database import Base, get_db

# Тестовая база данных
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@postgres:5432/test_db"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool,
)

AsyncTestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session", autouse=True)
async def create_test_tables():
    """Создаем таблицы один раз для всех тестов"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db_session():
    """Создаем сесию для каждого теста"""
    async with AsyncTestingSessionLocal() as session:
        try:
            yield session
        finally:
            # Just close the session without committing
            await session.close()


@pytest.fixture
def client(db_session):
    """Создаем test client с переопределенной зависимостью БД"""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# Фикстура event_loop для asyncio
@pytest.fixture(scope="session")
def event_loop():
    """Создаем event loop для сессии"""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()