# src/minifigures/routes.py
from fastapi import status, HTTPException, Depends, APIRouter, Form
from sqlalchemy.orm import Session
from src.minifigures.schemas import MinifigureCreate, MinifigureResponse, MinifigureUpdate, MinifigureDelete
from src.database import get_db
from src.minifigures.db import (
    get_db_minifigures,
    create_db_minifigure,
    get_db_one_minifigure,
    update_db_minifigure,
    delete_db_minifigure
)

router = APIRouter(
    prefix="/minifigures",
    tags=["Minifigures"]
)

@router.get(
    "/", 
    status_code=200, 
    response_model=list[MinifigureResponse],
    summary="Получить список минифигурок",
    description="Возвращает список всех минифигурок LEGO с возможностью пагинации и поиска"
)
async def get_minifigures(
    db: Session = Depends(get_db), 
    limit: int = 10, 
    offset: int = 0, 
    search: str | None = ""
):
    minifigures = get_db_minifigures(db, limit, offset, search)
    return minifigures

# Для фронтенда (JSON)
@router.post(
    "/json/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MinifigureResponse,
    summary="Создать новую минифигурку (JSON)",
    description="Создает новую минифигурку LEGO в коллекции (для фронтенда с JSON данными)"
)
async def create_minifigure(minifigure: MinifigureCreate, db: Session = Depends(get_db)):
    new_minifigure = create_db_minifigure(minifigure, db)
    return new_minifigure

# Для /docs (форма)
@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MinifigureResponse,
    summary="Создать новую минифигурку",
    description="Создает новую минифигурку LEGO в коллекции"
)
async def create_minifigure_form(
    minifigure_id: str = Form(
        description="Уникальный идентификатор минифигурки",
        example="hp150"
    ),
    character_name: str = Form(
        description="Имя персонажа",
        example="Гарри Поттер"
    ),
    name: str = Form(
        description="Название минифигурки",
        example="Harry Potter, Gryffindor Robe"
    ),
    face_photo_id: int | None = Form(
        default=None,
        description="ID главного фото минифигурки"
    ),
    db: Session = Depends(get_db)
):
    minifigure_data = MinifigureCreate(
        minifigure_id=minifigure_id,
        character_name=character_name,
        name=name,
        face_photo_id=face_photo_id
    )
    new_minifigure = create_db_minifigure(minifigure_data, db)
    return new_minifigure

@router.get(
    "/{minifigure_id}", 
    status_code=200, 
    response_model=MinifigureResponse,
    summary="Получить минифигурку по ID",
    description="Возвращает информацию о конкретной минифигурке LEGO по ее ID"
)
async def get_one_minifigure(minifigure_id: str, db: Session = Depends(get_db)):
    minifigure = get_db_one_minifigure(db, minifigure_id)
    return minifigure

# Для фронтенда (JSON)
@router.put(
    "/{minifigure_id}/json/", 
    status_code=200, 
    response_model=MinifigureResponse,
    summary="Обновить информацию о минифигурке (JSON)",
    description="Обновляет информацию о минифигурке LEGO по ее ID (для фронтенда с JSON данными)"
)
async def update_minifigure(minifigure_id: str, minifigure_update: MinifigureUpdate, db: Session = Depends(get_db)):
    updated_minifigure = update_db_minifigure(minifigure_id, minifigure_update, db)
    return updated_minifigure

# Для /docs (форма)
@router.put(
    "/{minifigure_id}", 
    status_code=200, 
    response_model=MinifigureResponse,
    summary="Обновить информацию о минифигурке",
    description="Обновляет информацию о минифигурке LEGO по ее ID"
)
async def update_minifigure_form(
    minifigure_id: str,
    character_name: str | None = Form(
        default=None,
        description="Имя персонажа",
        example="Гарри Поттер"
    ),
    name: str | None = Form(
        default=None,
        description="Название минифигурки",
        example="Harry Potter, Gryffindor Robe"
    ),
    face_photo_id: int | None = Form(
        default=None,
        description="ID главного фото минифигурки"
    ),
    db: Session = Depends(get_db)
):
    minifigure_data = MinifigureUpdate(
        character_name=character_name,
        name=name,
        face_photo_id=face_photo_id
    )
    updated_minifigure = update_db_minifigure(minifigure_id, minifigure_data, db)
    return updated_minifigure

# Для фронтенда (JSON)
@router.delete(
    "/json/", 
    status_code=200,
    summary="Удалить минифигурку (JSON)",
    description="Удаляет минифигурку LEGO из коллекции по ее ID (для фронтенда с JSON данными)"
)
async def delete_minifigure(minifigure_delete: MinifigureDelete, db: Session = Depends(get_db)):
    result = delete_db_minifigure(minifigure_delete, db)
    return result

# Для /docs (форма)
@router.delete(
    "/", 
    status_code=200,
    summary="Удалить минифигурку",
    description="Удаляет минифигурку LEGO из коллекции по ее ID"
)
async def delete_minifigure_form(
    minifigure_id: str = Form(
        description="Уникальный идентификатор минифигурки для удаления",
        example="hp150"
    ),
    db: Session = Depends(get_db)
):
    minifigure_delete = MinifigureDelete(minifigure_id=minifigure_id)
    result = delete_db_minifigure(minifigure_delete, db)
    return result