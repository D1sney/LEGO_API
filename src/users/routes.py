# src/users/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from src.users.schemas import UserCreate, UserResponse, UserUpdate, Token
from src.users.db import create_user, authenticate_user, update_user, get_user_by_id, get_users, revoke_refresh_token, revoke_all_user_refresh_tokens
from src.users.utils import create_access_token, create_refresh_token, verify_refresh_token, get_current_active_user, get_admin_user
from src.users.models import User, RefreshToken
from src.database import get_db
from src.config import settings

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"]
)

@router.post(
    "/register", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создание новой учетной записи пользователя"
)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    return create_user(db=db, user=user)

@router.post(
    "/login", 
    response_model=Token,
    summary="Вход в систему",
    description="Получение токена доступа и refresh токена для аутентифицированного пользователя"
)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Аутентификация пользователя и получение токенов"""
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создание access токена
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id, "username": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Создание refresh токена
    refresh_token, refresh_expires_at = create_refresh_token(db, user.user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds()),
        "refresh_expires_in": int((refresh_expires_at - datetime.now(timezone.utc)).total_seconds())
    }

@router.post(
    "/refresh-token",
    response_model=Token,
    summary="Обновление access токена",
    description="Получение нового access токена с использованием refresh токена"
)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Обновление access токена с помощью refresh токена"""
    db_token = verify_refresh_token(db, refresh_token)
    
    user = get_user_by_id(db, user_id=db_token.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный пользователь",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создание нового access токена
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id, "username": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Создание нового refresh токена (ротация)
    new_refresh_token, new_refresh_expires_at = create_refresh_token(db, user.user_id)
    
    # Аннулируем старый refresh токен
    revoke_refresh_token(db, refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds()),
        "refresh_expires_in": int((new_refresh_expires_at - datetime.now(timezone.utc)).total_seconds())
    }

@router.post(
    "/logout",
    summary="Выход из системы",
    description="Аннулирование refresh токена пользователя"
)
async def logout(
    refresh_token: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Выход из системы (аннулирование refresh токена)"""
    if not revoke_refresh_token(db, refresh_token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недействительный refresh токен"
        )
    
    return {"message": "Успешный выход из системы"}

@router.post(
    "/logout-all",
    summary="Выход из системы на всех устройствах",
    description="Аннулирование всех refresh токенов пользователя"
)
async def logout_all(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Выход из системы на всех устройствах (аннулирование всех refresh токенов)"""
    revoke_all_user_refresh_tokens(db, current_user.user_id)
    return {"message": "Успешный выход из системы на всех устройствах"}

@router.get(
    "/me", 
    response_model=UserResponse,
    summary="Получить информацию о текущем пользователе",
    description="Возвращает информацию о текущем аутентифицированном пользователе"
)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Получить информацию о текущем пользователе"""
    return current_user

@router.put(
    "/me", 
    response_model=UserResponse,
    summary="Обновить информацию о текущем пользователе",
    description="Обновление информации об аутентифицированном пользователе"
)
async def update_user_me(
    user_update: UserUpdate, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновить информацию о текущем пользователе"""
    return update_user(db=db, user_id=current_user.user_id, user_update=user_update)

@router.get(
    "/", 
    response_model=List[UserResponse],
    summary="Получить список всех пользователей",
    description="Возвращает список всех пользователей (только для администраторов)"
)
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Получить список пользователей (только для администраторов)"""
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get(
    "/{user_id}", 
    response_model=UserResponse,
    summary="Получить информацию о пользователе по ID",
    description="Возвращает информацию о пользователе по ID (только для администраторов)"
)
async def read_user(
    user_id: str, 
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Получить информацию о пользователе по ID (только для администраторов)"""
    db_user = get_user_by_id(db, user_id=user_id)
    
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Пользователь с ID {user_id} не найден"
        )
    
    return db_user
