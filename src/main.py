# src/main.py
from fastapi import FastAPI, Depends
from src.database import engine, get_db, Base
from src.sets.models import Set, SetMinifigure
from src.minifigures.models import Minifigure
from src.tags.models import Tag, SetTag, MinifigureTag
from src.photos.models import Photo
from sqlalchemy.orm import Session
from src.sets.routes import router as sets_router
from src.minifigures.routes import router as minifigures_router
from src.tags.routes import router as tags_router
from src.photos.routes import router as photos_router

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Подключаем маршруты
app.include_router(sets_router)
app.include_router(minifigures_router)
app.include_router(tags_router)
app.include_router(photos_router)

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    return {"message": "LEGO Collection API"}