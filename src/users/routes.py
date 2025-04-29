# src/users/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from src.users.schemas import UserCreate, UserResponse, UserUpdate, Token
from src.users.db import create_user, authenticate_user, update_user, get_user_by_id, get_users
from src.users.utils import create_access_token, get_current_active_user, get_admin_user
from src.users.models import User
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
    description="Получение токена доступа для аутентифицированного пользователя"
)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Аутентификация пользователя и получение токена"""
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создание данных для JWT токена
    token_data = {
        "sub": user.user_id,
        "username": user.username,
        "role": user.role
    }
    
    # Создание токена доступа
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=token_data, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

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
