# src/users/schemas.py
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя", example="john_doe")
    email: EmailStr = Field(..., description="Email пользователя", example="user@example.com")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Пароль пользователя (не менее 8 символов)")
    
    @field_validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Пароль должен содержать не менее 8 символов')
        # Здесь можно добавить дополнительные проверки на сложность пароля
        return v

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email пользователя", example="user@example.com")
    password: str = Field(..., description="Пароль пользователя")

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Время жизни access token в секундах
    refresh_expires_in: int  # Время жизни refresh token в секундах
    
class TokenData(BaseModel):
    user_id: str
    username: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[datetime] = None

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    
    @field_validator('password')
    def password_must_be_strong(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError('Пароль должен содержать не менее 8 символов')
        return v

class UserResponse(UserBase):
    user_id: str
    is_active: bool
    role: UserRole
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class EmailVerificationRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, description="6-значный код подтверждения")

class ResendVerificationCodeRequest(BaseModel):
    email: EmailStr = Field(..., description="Email для повторной отправки кода подтверждения")
