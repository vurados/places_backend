from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('password must contain at least one uppercase letter')
        return v

class UserOAuthCreate(BaseModel):
    provider: str  # google, telegram, vk
    provider_id: str
    access_token: str
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    login: str  # Может быть email или username
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenData(BaseModel):
    user_id: Optional[UUID] = None