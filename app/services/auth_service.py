from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_salt(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_password(password: str, salt: str) -> str:
    return pwd_context.hash(salt + password)

def verify_password(plain_password: str, hashed_password: str, salt: str) -> bool:
    return pwd_context.verify(salt + plain_password, hashed_password)

# Аутентификация пользователя по email и паролю
async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if not user or not user.password_hash or not user.password_salt:
        return None
    
    if not verify_password(password, user.password_hash, user.password_salt):
        return None
    
    return user

# Аутентификация пользователя по username и паролю
async def authenticate_user_by_username(db: AsyncSession, username: str, password: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    
    if not user or not user.password_hash or not user.password_salt:
        return None
    
    if not verify_password(password, user.password_hash, user.password_salt):
        return None
    
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Добавляем функцию для WebSocket аутентификации
async def get_current_user_ws(token: str, db: AsyncSession):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    return user