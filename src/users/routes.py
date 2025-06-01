# src/users/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from typing import List

from src.users.schemas import UserCreate, UserResponse, UserUpdate, Token, EmailVerificationRequest, ResendVerificationCodeRequest
from src.users.db import (
    create_user, authenticate_user, update_user, get_user_by_id, get_users, 
    revoke_refresh_token, revoke_all_user_refresh_tokens,
    create_email_verification, verify_email_code, complete_registration_from_verification, resend_verification_code
)
from src.users.utils import create_access_token, create_refresh_token, verify_refresh_token, get_current_active_user, get_admin_user
from src.users.models import User
from src.database import get_db
from src.config import settings
from src.logger import app_logger
from src.email.tasks import send_registration_email, send_verification_code_email

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"]
)

@router.post(
    "/register", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Завершить регистрацию после подтверждения email",
    description="Создание учетной записи пользователя после подтверждения email"
)
async def register(email_data: EmailVerificationRequest, db: Session = Depends(get_db)):
    """Завершение регистрации после подтверждения email"""
    
    try:
        new_user = complete_registration_from_verification(db, email_data.email)
        app_logger.info(f"User registered successfully: {new_user.username} ({new_user.email})")
        
        # Отправляем приветственное письмо
        try:
            send_registration_email.delay(new_user.email)
        except Exception as e:
            app_logger.warning(f"Failed to send welcome email to {new_user.email}: {e}")
        
        return new_user
        
    except HTTPException as exc:
        app_logger.warning(f"Registration failed for {email_data.email}: {exc.detail}")
        raise
    except Exception as e:
        app_logger.error(f"Unexpected error during registration: {email_data.email}, {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

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
        app_logger.warning(f"Login failed for {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создание access токена
    app_logger.info(f"User logged in: {user.username}")
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
        app_logger.warning(f"Logout failed: invalid refresh token for user {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недействительный refresh токен"
        )
    app_logger.info(f"User logged out: {current_user.username}")
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
    app_logger.info(f"User logged out from all devices: {current_user.username}")
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
    # Лишние строчки только для логов, можно выводить эти логи из db.py, но принято логировать бизнес логику именно на этом уровне, больше строчек, но за то понятнее
    try:
        updated_user = update_user(db=db, user_id=current_user.user_id, user_update=user_update)
        app_logger.info(f"User updated profile: {updated_user.username}")
        return updated_user
    except HTTPException as exc:
        app_logger.warning(f"Profile update failed for {current_user.username}: {exc.detail}")
        raise

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

@router.post(
    "/request-email-verification",
    summary="Запросить код подтверждения email для регистрации",
    description="Сохраняет данные пользователя и отправляет код подтверждения на email"
)
async def request_email_verification(user_data: UserCreate, db: Session = Depends(get_db)):
    """Запрос кода подтверждения email с сохранением данных пользователя"""
    
    try:
        verification = create_email_verification(db, user_data)
        
        # Отправляем код на email в фоновом режиме
        try:
            send_verification_code_email.delay(user_data.email, verification.verification_code)
            app_logger.info(f"Verification code email task queued for {user_data.email}")
        except Exception as e:
            app_logger.error(f"Failed to queue verification email task for {user_data.email}: {e}")
            raise HTTPException(status_code=500, detail="Не удалось отправить код подтверждения")
        
        return {"msg": "Код подтверждения отправлен на email", "email": user_data.email}
        
    except HTTPException as exc:
        app_logger.warning(f"Email verification request failed for {user_data.email}: {exc.detail}")
        raise
    except Exception as e:
        app_logger.error(f"Unexpected error during email verification request: {user_data.email}, {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.post(
    "/verify-email-code",
    summary="Подтвердить код верификации email",
    description="Проверяет код подтверждения и помечает email как верифицированный"
)
async def verify_email_code_endpoint(data: EmailVerificationRequest, db: Session = Depends(get_db)):
    """Проверка кода подтверждения email"""
    
    try:
        verification = verify_email_code(db, data.email, data.code)
        app_logger.info(f"Email verified: {data.email}")
        return {"msg": "Email успешно подтверждён. Можно завершить регистрацию.", "email": data.email}
        
    except HTTPException as exc:
        app_logger.warning(f"Email verification failed for {data.email}: {exc.detail}")
        raise
    except Exception as e:
        app_logger.error(f"Unexpected error during email verification: {data.email}, {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.post(
    "/resend-verification-code",
    summary="Повторная отправка кода подтверждения email",
    description="Отправляет новый код подтверждения на email (требует только email)"
)
async def resend_verification_code_endpoint(data: ResendVerificationCodeRequest, db: Session = Depends(get_db)):
    """Повторная отправка кода подтверждения email"""
    
    try:
        verification = resend_verification_code(db, data.email)
        
        # Отправляем новый код на email в фоновом режиме
        try:
            send_verification_code_email.delay(data.email, verification.verification_code)
            app_logger.info(f"Resend verification code email task queued for {data.email}")
        except Exception as e:
            app_logger.error(f"Failed to queue resend verification email task for {data.email}: {e}")
            raise HTTPException(status_code=500, detail="Не удалось отправить код подтверждения")
        
        return {"msg": "Новый код подтверждения отправлен на email", "email": data.email}
        
    except HTTPException as exc:
        app_logger.warning(f"Resend verification code failed for {data.email}: {exc.detail}")
        raise
    except Exception as e:
        app_logger.error(f"Unexpected error during resend verification code: {data.email}, {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
