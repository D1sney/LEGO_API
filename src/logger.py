# src/logger.py
import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
import time

# Создаём директорию для логов
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Определяем уровень логирования через переменную окружения
log_level = logging.DEBUG if os.getenv("ENV") == "development" else logging.INFO

def setup_logger(name, log_level=log_level):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    if logger.handlers:
        return logger
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # В консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    # В файл
    file_handler = RotatingFileHandler(
        logs_dir / f"{name}.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

app_logger = setup_logger("lego_api")
request_logger = setup_logger("lego_api.requests")
db_logger = setup_logger("lego_api.db")

def log_db_operation(func):
    """
    Декоратор для логирования операций с базой данных:
    - Логирует имя функции, время выполнения и ошибки.
    Используется для функций, работающих с БД.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            db_logger.info(f"DB operation {func.__name__} completed in {round((time.time() - start_time) * 1000, 2)} ms")
            return result
        except Exception as exc:
            db_logger.error(f"DB operation {func.__name__} failed: {str(exc)}")
            raise
    return wrapper 