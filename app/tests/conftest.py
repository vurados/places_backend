import asyncio
import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

import logging

# Reduce SQLAlchemy logging during tests
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

# Устанавливаем флаг тестирования
os.environ["TESTING"] = "True"

# Устанавливаем переменные окружения, если они не заданы
if not os.getenv("DB_HOST"):
    os.environ["DB_HOST"] = "localhost"
if not os.getenv("DB_PORT"):
    os.environ["DB_PORT"] = "5432"
if not os.getenv("DB_USER"):
    os.environ["DB_USER"] = "test_user"
if not os.getenv("DB_PASSWORD"):
    os.environ["DB_PASSWORD"] = "test_password"
if not os.getenv("DB_NAME"):
    os.environ["DB_NAME"] = "test_db"
if not os.getenv("REDIS_HOST"):
    os.environ["REDIS_HOST"] = "redis"
if not os.getenv("REDIS_PORT"):
    os.environ["REDIS_PORT"] = "6379"
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "test_secret_key_for_tests"

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from core.database import Base, get_db

# Тестовая база данных
# Тестовая база данных
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

TEST_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

@pytest.fixture(scope="function")
async def async_engine():
    """Создаем новый асинхронный движок для каждой тестовой функции."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        poolclass=NullPool,
    )
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
def async_session_maker(async_engine):
    """Создаем новый sessionmaker для каждой тестовой функции."""
    return sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

@pytest.fixture(scope="function", autouse=True)
async def create_test_tables(async_engine):
    """Создаем и удаляем таблицы для каждой тестовой функции."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db_session(async_session_maker):
    """Создаем сессию для каждого теста."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture
def client(db_session):
    """Создаем test client с переопределенной зависимостью БД"""
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# Фикстура event_loop для asyncio
@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test function."""
    loop = asyncio.new_event_loop()
    yield loop
    try:
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        loop.close()