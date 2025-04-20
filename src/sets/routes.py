# src/sets/routes.py
from fastapi import status, HTTPException, Depends, APIRouter, Request, Form
from sqlalchemy.orm import Session
from typing import Optional
from src.sets.schemas import SetCreate, SetResponse, SetUpdate, SetDelete, SetMinifigureCreate, SetMinifigureResponse, SetMinifigureDelete
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

router = APIRouter(
    prefix="/sets",
    tags=["Sets"]
)

@router.get(
    "/",
    status_code=200,
    response_model=list[SetResponse],
    summary="Получить список наборов LEGO", 
    description="Возвращает список всех наборов LEGO с возможностью пагинации и поиска"
)
async def get_sets(
    db: Session = Depends(get_db), 
    limit: int = 10, 
    offset: int = 0, 
    search: str | None = ""
):
    sets = get_db_sets(db, limit, offset, search)
    return sets

# Для фронтенда (JSON)
@router.post(
    "/json/",
    status_code=status.HTTP_201_CREATED,
    response_model=SetResponse,
    summary="Создать новый набор LEGO (JSON)",
    description="Создает новый набор LEGO в коллекции (для фронтенда с JSON данными)"
)
async def create_set(set: SetCreate, db: Session = Depends(get_db)):
    new_set = create_db_set(set, db)
    return new_set

# Для /docs (форма)
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=SetResponse,
    summary="Создать новый набор LEGO",
    description="Создает новый набор LEGO в коллекции"
)
async def create_set_form(
    name: str = Form(
        default="Хогвартс: Астрономическая башня",
        description="Название набора LEGO"
    ),
    piece_count: int = Form(
        default=971,
        description="Количество деталей в наборе"
    ),
    release_year: int = Form(
        default=2020,
        description="Год выпуска набора"
    ),
    theme: str = Form(
        default="Harry Potter",
        description="Основная тема набора"
    ),
    sub_theme: str | None = Form(
        default="Hogwarts",
        description="Подтема набора (если есть)"
    ),
    price: float = Form(
        default=8999.99,
        description="Цена набора в рублях"
    ),
    face_photo_id: Optional[int] = Form(
        default=None,
        description="ID главного фото набора (оставьте пустым для null)"
    ),
    db: Session = Depends(get_db)
):
    set_data = SetCreate(
        name=name,
        piece_count=piece_count,
        release_year=release_year,
        theme=theme,
        sub_theme=sub_theme,
        price=price,
        face_photo_id=face_photo_id
    )
    new_set = create_db_set(set_data, db)
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

# Для фронтенда (JSON)
@router.put(
    "/{set_id}/json/",
    status_code=200,
    response_model=SetResponse,
    summary="Обновить информацию о наборе LEGO (JSON)",
    description="Обновляет информацию о наборе LEGO по его ID (для фронтенда с JSON данными)"
)
async def update_set(set_id: int, set_update: SetUpdate, db: Session = Depends(get_db)):
    updated_set = update_db_set(set_id, set_update, db)
    return updated_set

# Для /docs (форма)
@router.put(
    "/{set_id}",
    status_code=200,
    response_model=SetResponse,
    summary="Обновить информацию о наборе LEGO",
    description="Обновляет информацию о наборе LEGO по его ID"
)
async def update_set_form(
    set_id: int,
    name: str | None = Form(
        default=None,
        description="Название набора LEGO"
    ),
    piece_count: int | None = Form(
        default=None,
        description="Количество деталей в наборе"
    ),
    release_year: int | None = Form(
        default=None,
        description="Год выпуска набора"
    ),
    theme: str | None = Form(
        default=None,
        description="Основная тема набора"
    ),
    sub_theme: str | None = Form(
        default=None,
        description="Подтема набора (если есть)"
    ),
    price: float | None = Form(
        default=None,
        description="Цена набора в рублях"
    ),
    face_photo_id: Optional[int] = Form(
        default=None,
        description="ID главного фото набора (оставьте пустым для null)"
    ),
    db: Session = Depends(get_db)
):
    set_data = SetUpdate(
        name=name,
        piece_count=piece_count,
        release_year=release_year,
        theme=theme,
        sub_theme=sub_theme,
        price=price,
        face_photo_id=face_photo_id
    )
    updated_set = update_db_set(set_id, set_data, db)
    return updated_set

# Для фронтенда (JSON)
@router.delete(
    "/json/",
    status_code=200,
    summary="Удалить набор LEGO (JSON)",
    description="Удаляет набор LEGO из коллекции по его ID (для фронтенда с JSON данными)"
)
async def delete_set(set_delete: SetDelete, db: Session = Depends(get_db)):
    result = delete_db_set(set_delete, db)
    return result

# Для /docs (форма)
@router.delete(
    "/",
    status_code=200,
    summary="Удалить набор LEGO",
    description="Удаляет набор LEGO из коллекции по его ID"
)
async def delete_set_form(
    set_id: int = Form(
        description="Уникальный идентификатор набора для удаления"
    ),
    db: Session = Depends(get_db)
):
    set_delete = SetDelete(set_id=set_id)
    result = delete_db_set(set_delete, db)
    return result

# Эндпоинты для SetMinifigure

# Для фронтенда (JSON)
@router.post(
    "/minifigures/json/",
    status_code=status.HTTP_201_CREATED,
    response_model=SetMinifigureResponse,
    summary="Добавить минифигурку в набор (JSON)",
    description="Связывает минифигурку с набором LEGO (для фронтенда с JSON данными)"
)
async def create_set_minifigure(set_minifigure: SetMinifigureCreate, db: Session = Depends(get_db)):
    new_set_minifigure = create_db_set_minifigure(set_minifigure, db)
    return new_set_minifigure

# Для /docs (форма)
@router.post(
    "/minifigures/",
    status_code=status.HTTP_201_CREATED,
    response_model=SetMinifigureResponse,
    summary="Добавить минифигурку в набор",
    description="Связывает минифигурку с набором LEGO"
)
async def create_set_minifigure_form(
    set_id: int = Form(
        description="ID набора LEGO"
    ),
    minifigure_id: str = Form(
        description="ID минифигурки LEGO"
    ),
    db: Session = Depends(get_db)
):
    set_minifigure = SetMinifigureCreate(
        set_id=set_id,
        minifigure_id=minifigure_id
    )
    new_set_minifigure = create_db_set_minifigure(set_minifigure, db)
    return new_set_minifigure

# Для фронтенда (JSON)
@router.delete(
    "/minifigures/json/",
    status_code=200,
    summary="Удалить минифигурку из набора (JSON)",
    description="Удаляет связь между минифигуркой и набором LEGO (для фронтенда с JSON данными)"
)
async def delete_set_minifigure(set_minifigure_delete: SetMinifigureDelete, db: Session = Depends(get_db)):
    result = delete_db_set_minifigure(set_minifigure_delete, db)
    return result

# Для /docs (форма)
@router.delete(
    "/minifigures/",
    status_code=200,
    summary="Удалить минифигурку из набора",
    description="Удаляет связь между минифигуркой и набором LEGO"
)
async def delete_set_minifigure_form(
    set_id: int = Form(
        description="ID набора LEGO для удаления связи"
    ),
    minifigure_id: str = Form(
        description="ID минифигурки LEGO для удаления связи"
    ),
    db: Session = Depends(get_db)
):
    set_minifigure_delete = SetMinifigureDelete(
        set_id=set_id,
        minifigure_id=minifigure_id
    )
    result = delete_db_set_minifigure(set_minifigure_delete, db)
    return result