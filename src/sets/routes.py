# src/sets/routes.py
from fastapi import status, HTTPException, Depends, APIRouter, Request, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from src.sets.schemas import SetCreate, SetResponse, SetUpdate, SetDelete, SetMinifigureCreate, SetMinifigureResponse, SetMinifigureDelete, SetFilter
from src.database import get_db
from src.sets.db import (
    get_db_sets,
    create_db_set,
    get_db_one_set,
    update_db_set,
    delete_db_set,
    create_db_set_minifigure,
    delete_db_set_minifigure
)
from src.users.utils import get_current_active_user

router = APIRouter(
    prefix="/sets",
    tags=["Sets"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get(
    "/",
    status_code=200,
    response_model=list[SetResponse],
    summary="Получить список наборов LEGO", 
    description="Возвращает список всех наборов LEGO с возможностью пагинации, поиска, фильтрации по тегу, цене и количеству деталей"
)
async def get_sets(filter: SetFilter = Depends(), db: Session = Depends(get_db)):
    """
    Получить список наборов с фильтрацией и пагинацией.
    """
    sets = get_db_sets(
        db=db,
        limit=filter.limit,
        offset=filter.offset,
        search=filter.search,
        tag_names=filter.tag_names,
        tag_logic=filter.tag_logic,
        min_price=filter.min_price,
        max_price=filter.max_price,
        min_piece_count=filter.min_piece_count,
        max_piece_count=filter.max_piece_count
    )
    return sets

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=SetResponse,
    summary="Создать новый набор LEGO",
    description="Создает новый набор LEGO в коллекции"
)
async def create_set(set: SetCreate, db: Session = Depends(get_db)):
    new_set = create_db_set(set, db)
    return new_set

@router.get(
    "/{set_id}",
    status_code=200,
    response_model=SetResponse,
    summary="Получить набор LEGO по ID",
    description="Возвращает информацию о конкретном наборе LEGO по его ID"
)
async def get_one_set(set_id: int, db: Session = Depends(get_db)):
    set = get_db_one_set(db, set_id)
    return set

@router.put(
    "/{set_id}/",
    status_code=200,
    response_model=SetResponse,
    summary="Обновить информацию о наборе LEGO",
    description="Обновляет информацию о наборе LEGO по его ID"
)
async def update_set(set_id: int, set_update: SetUpdate, db: Session = Depends(get_db)):
    updated_set = update_db_set(set_id, set_update, db)
    return updated_set

@router.delete(
    "/",
    status_code=200,
    summary="Удалить набор LEGO",
    description="Удаляет набор LEGO из коллекции по его ID"
)
async def delete_set(set_delete: SetDelete, db: Session = Depends(get_db)):
    result = delete_db_set(set_delete, db)
    return result

# Эндпоинты для SetMinifigure

@router.post(
    "/minifigures/",
    status_code=status.HTTP_201_CREATED,
    response_model=SetMinifigureResponse,
    summary="Добавить минифигурку в набор",
    description="Связывает минифигурку с набором LEGO"
)
async def create_set_minifigure(set_minifigure: SetMinifigureCreate, db: Session = Depends(get_db)):
    new_set_minifigure = create_db_set_minifigure(set_minifigure, db)
    return new_set_minifigure

@router.delete(
    "/minifigures/",
    status_code=200,
    summary="Удалить минифигурку из набора",
    description="Удаляет связь между минифигуркой и набором LEGO"
)
async def delete_set_minifigure(set_minifigure_delete: SetMinifigureDelete, db: Session = Depends(get_db)):
    result = delete_db_set_minifigure(set_minifigure_delete, db)
    return result