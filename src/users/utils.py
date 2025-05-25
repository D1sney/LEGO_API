# src/users/utils.py
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import uuid
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import random
import string

from src.config import settings
from src.database import get_db
from src.users.models import User, RefreshToken
from src.logger import app_logger

# Настройка для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Создание access токена"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        app_logger.debug(f"Access token создан для пользователя {data.get('username', 'unknown')}")
        return encoded_jwt
    except Exception as e:
        app_logger.error(f"Ошибка при создании access токена: {e}")
        raise

def create_refresh_token(db: Session, user_id: str) -> tuple[str, datetime]:
    """Создание refresh токена и сохранение его в базе данных"""
    token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    db_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    app_logger.debug(f"Refresh token создан для пользователя {user_id}")
    return token, expires_at

def verify_refresh_token(db: Session, token: str) -> RefreshToken:
    """Проверка refresh токена"""
    db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if not db_token:
        app_logger.warning(f"Попытка использовать несуществующий refresh токен: {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный refresh токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if db_token.revoked:
        app_logger.warning(f"Попытка использовать отозванный refresh токен: {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh токен был аннулирован",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if db_token.expires_at < datetime.now(timezone.utc):
        app_logger.info(f"Попытка использовать истекший refresh токен: {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия refresh токена истёк",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return db_token

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Получение текущего пользователя по access токену"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Декодирование токена
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            app_logger.warning("Access токен не содержит user_id (sub)")
            raise credentials_exception
    except JWTError as e:
        app_logger.warning(f"Ошибка декодирования access токена: {e}")
        raise credentials_exception
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        app_logger.warning(f"Пользователь с id {user_id} не найден по access токену")
        raise credentials_exception
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Проверка, что текущий пользователь активен"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неактивный пользователь"
        )
    return current_user

def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Проверка, что текущий пользователь — администратор"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    return current_user

def generate_verification_code(length: int = 6) -> str:
    code = ''.join(random.choices(string.digits, k=length))
    app_logger.debug(f"Сгенерирован код подтверждения: {code}")
    return code
