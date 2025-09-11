import pytest
from models.user import User
from services.auth_service import verify_password, hash_password, generate_salt

# Тест хеширования паролей
@pytest.mark.asyncio
async def test_password_hashing():
    password = "TestPassword123"
    salt = generate_salt()
    hashed = hash_password(password, salt)
    
    # Проверяем что пароль верифицируется
    assert verify_password(password, hashed, salt)
    
    # Проверяем что неправильный пароль не проходит
    assert not verify_password("WrongPassword", hashed, salt)

# Тест создания пользователя
@pytest.mark.asyncio
async def test_user_creation():
    user = User(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User"
    )
    
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert not user.is_verified
    assert user.is_active