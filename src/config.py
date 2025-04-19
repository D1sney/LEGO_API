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
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    BASE_URL: str

    class Config:
        # Определяем путь к .env файлу в зависимости от текущей директории
        if os.path.exists(".env"):
            env_file = ".env"
        else:
            env_file = "../.env"

settings = Settings()