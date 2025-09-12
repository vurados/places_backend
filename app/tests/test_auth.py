import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.services.auth_service import hash_password, generate_salt

@pytest.mark.asyncio
async def test_register_user(client, db_session: AsyncSession):
    """Тест регистрации пользователя"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "password": "SecurePass123",
        "confirm_password": "SecurePass123"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "password_hash" not in data

@pytest.mark.asyncio
async def test_register_user_weak_password(client):
    """Тест регистрации со слабым паролем"""
    user_data = {
        "email": "test2@example.com",
        "username": "testuser2",
        "password": "weak",
        "confirm_password": "weak"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_login_user(client, db_session: AsyncSession):
    """Тест входа пользователя"""
    # Сначала регистрируем пользователя
    salt = generate_salt()
    password_hash = hash_password("SecurePass123", salt)
    
    user = User(
        email="login@example.com",
        username="loginuser",
        password_hash=password_hash,
        password_salt=salt,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    
    # Тестируем логин
    login_data = {"login": "login@example.com", "password": "SecurePass123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_login_user_wrong_password(client, db_session: AsyncSession):
    """Тест входа с неправильным паролем"""
    salt = generate_salt()
    password_hash = hash_password("SecurePass123", salt)
    
    user = User(
        email="wrong@example.com",
        username="wronguser",
        password_hash=password_hash,
        password_salt=salt,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    
    login_data = {"login": "wrong@example.com", "password": "WrongPassword"}
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED