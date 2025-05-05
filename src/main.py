# src/main.py
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from src.database import engine, get_db, Base
from src.sets.models import Set, SetMinifigure
from src.minifigures.models import Minifigure
from src.tags.models import Tag, SetTag, MinifigureTag
from src.photos.models import Photo
from src.users.models import User
from sqlalchemy.orm import Session
from src.sets.routes import router as sets_router
from src.minifigures.routes import router as minifigures_router
from src.tags.routes import router as tags_router
from src.photos.routes import router as photos_router
from src.users.routes import router as users_router
from fastapi.middleware.cors import CORSMiddleware

# Создаем таблицы в базе данных
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LEGO Collection API",
    description="API для управления персональной коллекцией LEGO наборов и минифигурок",
    version="0.1.0",
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

# Подключаем папку static для раздачи файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

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

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    return {"message": "LEGO Collection API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
