# src/users/db.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy import update

from src.users.models import User, RefreshToken, EmailVerification
from src.users.schemas import UserCreate, UserUpdate
from src.users.utils import get_password_hash, verify_password, generate_verification_code
from src.logger import app_logger, log_db_operation
from src.config import settings

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

# Email Verification functions

@log_db_operation
def create_email_verification(db: Session, user: UserCreate) -> EmailVerification:
    """Создать запись верификации email"""
    # Проверяем, что пользователь с таким email НЕ зарегистрирован
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегистрирован"
        )
    
    # Проверяем, что username не занят
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Имя пользователя уже занято"
        )
    
    # Удаляем старую запись верификации для этого email (если есть)
    db.query(EmailVerification).filter(EmailVerification.email == user.email).delete()
    
    # Генерируем код и создаем запись верификации
    code = generate_verification_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFICATION_EXPIRE_MINUTES)
    
    verification = EmailVerification(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
        verification_code=code,
        expires_at=expires_at,
        verified=False
    )
    
    try:
        db.add(verification)
        db.commit()
        db.refresh(verification)
        return verification
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании запроса верификации"
        )

@log_db_operation
def verify_email_code(db: Session, email: str, code: str) -> EmailVerification:
    """Проверить код верификации email"""
    verification = db.query(EmailVerification).filter(
        EmailVerification.email == email
    ).first()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Запрос на верификацию не найден"
        )
    
    # Проверяем срок действия
    if datetime.now(timezone.utc) > verification.expires_at:
        # Удаляем просроченную запись
        db.query(EmailVerification).filter(EmailVerification.email == email).delete()
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Срок действия кода истёк. Запросите новый код."
        )
    
    if verification.verification_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный код подтверждения"
        )
    
    # Помечаем как верифицированный
    verification.verified = True
    db.commit()
    db.refresh(verification)
    return verification

@log_db_operation
def complete_registration_from_verification(db: Session, email: str) -> User:
    """Завершить регистрацию после подтверждения email"""
    # Ищем верифицированную запись
    verification = db.query(EmailVerification).filter(
        EmailVerification.email == email,
        EmailVerification.verified == True
    ).first()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email не подтверждён. Сначала пройдите верификацию."
        )
    
    # Проверяем, что пользователь ещё не зарегистрирован (двойная проверка)
    if get_user_by_email(db, email):
        # Удаляем запись верификации
        db.query(EmailVerification).filter(EmailVerification.email == email).delete()
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь уже зарегистрирован"
        )
    
    try:
        # Создаём пользователя из сохранённых данных
        new_user = User(
            email=verification.email,
            username=verification.username,
            hashed_password=verification.hashed_password,
            is_active=True
        )
        db.add(new_user)
        
        # Удаляем запись верификации
        db.query(EmailVerification).filter(EmailVerification.email == email).delete()
        
        db.commit()
        db.refresh(new_user)
        return new_user
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании пользователя"
        )