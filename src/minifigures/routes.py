# src/minifigures/routes.py
from fastapi import status, HTTPException, Depends, APIRouter, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from src.minifigures.schemas import MinifigureCreate, MinifigureResponse, MinifigureUpdate, MinifigureDelete, MinifigureFilter
from src.database import get_db
from src.minifigures.db import (
    get_db_minifigures,
    create_db_minifigure,
    get_db_one_minifigure,
    update_db_minifigure,
    delete_db_minifigure
)
from src.users.utils import get_current_active_user
from src.logger import app_logger

router = APIRouter(
    prefix="/minifigures",
    tags=["Minifigures"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get(
    "/", 
    status_code=200, 
    response_model=list[MinifigureResponse],
    summary="Получить список минифигурок",
    description="Возвращает список всех минифигурок LEGO с возможностью пагинации, поиска, фильтрации по тегу и цене"
)
async def get_minifigures(filter: MinifigureFilter = Depends(), db: Session = Depends(get_db)):
    """
    Получить список минифигурок с фильтрацией и пагинацией.
    """
    minifigures = get_db_minifigures(
        db=db,
        limit=filter.limit,
        offset=filter.offset,
        search=filter.search,
        tag_names=filter.tag_names,
        tag_logic=filter.tag_logic,
        min_price=filter.min_price,
        max_price=filter.max_price
    )
    app_logger.info(f"Получено {len(minifigures)} минифигурок (фильтр: {filter.dict()})")
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
    app_logger.info(f"Создана минифигурка: {new_minifigure.name} (ID: {new_minifigure.minifigure_id})")
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
    app_logger.info(f"Обновлена минифигурка ID: {minifigure_id}")
    return updated_minifigure

@router.delete(
    "/", 
    status_code=200,
    summary="Удалить минифигурку",
    description="Удаляет минифигурку LEGO из коллекции по ее ID"
)
async def delete_minifigure(minifigure_delete: MinifigureDelete, db: Session = Depends(get_db)):
    result = delete_db_minifigure(minifigure_delete, db)
    app_logger.info(f"Удалена минифигурка ID: {minifigure_delete.minifigure_id}")
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
    app_logger.info(f"Получена минифигурка ID: {minifigure_id}")
    return minifigure