# src/main.py
import os
from datetime import datetime
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from src.database import engine, get_db, Base
from src.sets.models import Set, SetMinifigure
from src.minifigures.models import Minifigure
from src.tags.models import Tag, SetTag, MinifigureTag
from src.photos.models import Photo
from src.users.models import User
from src.tournaments.models import Tournament, TournamentParticipant, TournamentPair, TournamentVote
from src.winners.models import TournamentWinner
from sqlalchemy.orm import Session
from src.sets.routes import router as sets_router
from src.minifigures.routes import router as minifigures_router
from src.tags.routes import router as tags_router
from src.photos.routes import router as photos_router
from src.users.routes import router as users_router
from src.tournaments.routes import router as tournaments_router
from src.winners.routes import router as winners_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from src.middleware import LoggingMiddleware
from src.logger import app_logger


# Middleware для обработки X-Forwarded заголовков от reverse proxy
class ProxyHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Обрабатываем X-Forwarded-Proto заголовок от nginx
        forwarded_proto = request.headers.get("x-forwarded-proto")
        if forwarded_proto:
            request.scope["scheme"] = forwarded_proto
        
        # Обрабатываем X-Forwarded-Host заголовок от nginx
        forwarded_host = request.headers.get("x-forwarded-host")
        if forwarded_host:
            request.scope["server"] = (forwarded_host, None)
        
        response = await call_next(request)
        return response


# Создаем таблицы в базе данных
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LEGO Collection API",
    description="API для управления персональной коллекцией LEGO наборов и минифигурок",
    version="0.1.0",
    root_path="/api",
    docs_url="/docs" if os.getenv("ENV") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENV") == "development" else None,
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Ivan Samsonov",
        "url": "https://github.com/D1sney",
        "email": "ivan36samsonov@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Логгирование запуска приложения
app_logger.info("Запуск приложения LEGO Collection API")

# Добавляем middleware для обработки reverse proxy заголовков (ВАЖНО: первым!)
app.add_middleware(ProxyHeadersMiddleware)

# Добавляем middleware для доверенных хостов
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Добавляем middleware для логирования
app.add_middleware(LoggingMiddleware)

# Подключаем папку static для раздачи файлов
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене лучше указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем маршруты
app.include_router(sets_router)
app.include_router(minifigures_router)
app.include_router(tags_router)
app.include_router(photos_router)
app.include_router(users_router)
app.include_router(tournaments_router)
app.include_router(winners_router)

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    app_logger.info("Запрос к корневому эндпоинту")
    return {"message": "LEGO Collection API"}

@app.get("/health")
def health_check():
    """Health check endpoint для Docker и мониторинга"""
    return {"status": "healthy", "service": "LEGO Collection API", "timestamp": datetime.now().isoformat()}

# Обработчик для перехвата необработанных исключений
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    app_logger.error(f"Необработанное исключение: {str(exc)} | url={request.url} | method={request.method} | type={type(exc).__name__}")
    return {"detail": "Внутренняя ошибка сервера"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
