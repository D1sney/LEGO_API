# src/users/db.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import update

from src.users.models import User, RefreshToken
from src.users.schemas import UserCreate, UserUpdate
from src.users.utils import get_password_hash, verify_password
from src.logger import app_logger, log_db_operation

@log_db_operation
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Получить пользователя по email"""
    return db.query(User).filter(User.email == email).first()

@log_db_operation
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Получить пользователя по имени пользователя"""
    return db.query(User).filter(User.username == username).first()

@log_db_operation
def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Получить пользователя по ID"""
    return db.query(User).filter(User.user_id == user_id).first()

@log_db_operation
def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Получить список пользователей"""
    return db.query(User).offset(skip).limit(limit).all()

@log_db_operation
def create_user(db: Session, user: UserCreate) -> User:
    """Создать нового пользователя"""
    # Проверка на существование пользователя с таким email
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    # Проверка на существование пользователя с таким username
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    # Создание хеша пароля
    hashed_password = get_password_hash(user.password)
    
    # Создание объекта пользователя
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        # Лог этой ошибки есть в routes.py, логирование бизнес логики не должно быть в db.py
        # app_logger.error(f"Error creating user: {str(e)}")
        if isinstance(e.orig, UniqueViolation):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка уникальности данных при создании пользователя"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка при создании пользователя"
            )

@log_db_operation
def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Аутентификация пользователя"""
    user = get_user_by_email(db, email)
    
    # Если пользователя нет или пароль неверный
    if not user or not verify_password(password, user.hashed_password):
        # Если пользователь существует, увеличиваем счетчик попыток входа
        if user:
            user.login_attempts += 1
            db.commit()
            
            # Можно добавить блокировку пользователя после определенного числа попыток
            if user.login_attempts >= 5:
                user.is_active = False
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Учетная запись заблокирована из-за превышения количества попыток входа"
                )
        return None
    
    # Сбрасываем счетчик попыток при успешном входе
    user.login_attempts = 0
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    return user

@log_db_operation
def update_user(db: Session, user_id: str, user_update: UserUpdate) -> User:
    """Обновить информацию о пользователе"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )
    # Получаем все поля для обновления
    update_data = user_update.dict(exclude_unset=True)
    
    # Если обновляется email, проверяем его уникальность
    if 'email' in update_data and update_data['email'] != db_user.email:
        if get_user_by_email(db, update_data['email']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
    
    # Если обновляется username, проверяем его уникальность
    if 'username' in update_data and update_data['username'] != db_user.username:
        if get_user_by_username(db, update_data['username']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким именем уже существует"
            )
    
    # Если обновляется пароль, хешируем его
    if 'password' in update_data:
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
    try:
        # Обновляем все поля
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        # Лог этой ошибки есть в routes.py, логирование бизнес логики не должно быть в db.py
        # app_logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при обновлении пользователя"
        )

@log_db_operation
def revoke_refresh_token(db: Session, token: str) -> bool:
    """Аннулировать refresh токен"""
    db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if not db_token:
        return False
    db_token.revoked = True
    db.commit()
    return True

@log_db_operation
def revoke_all_user_refresh_tokens(db: Session, user_id: str) -> None:
    """Аннулировать все refresh токены пользователя"""
    result = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked == False
    ).update({"revoked": True})
    db.commit()