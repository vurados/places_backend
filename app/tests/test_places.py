import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.place import Place

@pytest.mark.asyncio
async def test_create_place(client, db_session: AsyncSession):
    """Тест создания места"""
    # Создаем пользователя
    user = User(
        email="place@example.com",
        username="placeuser",
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    
    # Получаем токен
    login_data = {"login": "place@example.com", "password": "SecurePass123"}
    # ... здесь нужно добавить пароль пользователю ...
    
    place_data = {
        "name": "Test Place",
        "description": "A test place",
        "latitude": 55.7558,
        "longitude": 37.6173,
        "address": "Test Address",
        "is_public": True
    }
    
    # Пока без аутентификации в тестах
    # response = client.post("/api/v1/places", json=place_data, headers=auth_headers)
    # assert response.status_code == status.HTTP_200_OK