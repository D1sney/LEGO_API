# src/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    EMAIL_VERIFICATION_EXPIRE_MINUTES: int = 5
    EMAIL_VERIFICATION_RESEND_INTERVAL_MINUTES: int = 2
    BASE_URL: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAIL_FROM: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    class Config:
        # Определяем путь к .env файлу в зависимости от текущей директории
        if os.path.exists(".env"):
            env_file = ".env"
        else:
            env_file = "../.env"

settings = Settings()