# src/minifigures/routes.py
from fastapi import status, HTTPException, Depends, APIRouter, Form
from sqlalchemy.orm import Session
from typing import Optional
from src.minifigures.schemas import MinifigureCreate, MinifigureResponse, MinifigureUpdate, MinifigureDelete, MinifigureFilter
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
    description="Возвращает список всех минифигурок LEGO с возможностью пагинации, поиска и фильтрации по тегу"
)
async def get_minifigures(
    filter: MinifigureFilter = Depends(),
    db: Session = Depends(get_db)
):
    minifigures = get_db_minifigures(db, filter.limit, filter.offset, filter.search, filter.tag_name)
    return minifigures

@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MinifigureResponse,
    summary="Создать новую минифигурку",
    description="Создает новую минифигурку LEGO в коллекции"
)
async def create_minifigure(minifigure: MinifigureCreate, db: Session = Depends(get_db)):
    new_minifigure = create_db_minifigure(minifigure, db)
    return new_minifigure

@router.put(
    "/{minifigure_id}/", 
    status_code=200, 
    response_model=MinifigureResponse,
    summary="Обновить информацию о минифигурке",
    description="Обновляет информацию о минифигурке LEGO по ее ID"
)
async def update_minifigure(minifigure_id: str, minifigure_update: MinifigureUpdate, db: Session = Depends(get_db)):
    updated_minifigure = update_db_minifigure(minifigure_id, minifigure_update, db)
    return updated_minifigure

@router.delete(
    "/", 
    status_code=200,
    summary="Удалить минифигурку",
    description="Удаляет минифигурку LEGO из коллекции по ее ID"
)
async def delete_minifigure(minifigure_delete: MinifigureDelete, db: Session = Depends(get_db)):
    result = delete_db_minifigure(minifigure_delete, db)
    return result

@router.get(
    "/{minifigure_id}/", 
    status_code=200, 
    response_model=MinifigureResponse,
    summary="Получить минифигурку по ID",
    description="Возвращает информацию о конкретной минифигурке LEGO по ее ID"
)
async def get_one_minifigure(minifigure_id: str, db: Session = Depends(get_db)):
    minifigure = get_db_one_minifigure(db, minifigure_id)
    return minifigure