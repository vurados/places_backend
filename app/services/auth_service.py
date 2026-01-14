import string
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.config import settings
from models.user import User



def generate_salt(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_password(password: str, salt: str) -> str:
    # Use bcrypt to hash the password combined with the salt
    # Note: bcrypt handles its own salting internally, but since we have an existing "salt" parameter 
    # and to match previous logic where salt was prepended, we keep the signature but combine them.
    # Ideally, we'd rely solely on bcrypt's salt, but for backward compat/logic we hash the combo.
    # However, standard bcrypt doesn't take an external salt string for the input, it generates one.
    # The original code did: pwd_context.hash(salt + password)
    # This suggests the "salt" arg was acted as a pepper or pre-salt.
    # We will replicate: hash(salt + password)
    
    password_bytes = (salt + password).encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str, salt: str) -> bool:
    password_bytes = (salt + plain_password).encode('utf-8')
    try:
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except ValueError:
        return False

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Получает текущего пользователя из JWT токена
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"No email in payload {token}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"JWTError {token}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Ищем пользователя в базе данных

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User was not found with email {email}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

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
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
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