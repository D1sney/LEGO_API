# src/photos/routes.py
from fastapi import status, HTTPException, Depends, APIRouter, Form
from sqlalchemy.orm import Session
from src.photos.schemas import PhotoCreate, PhotoResponse, PhotoUpdate, PhotoDelete
from src.database import get_db
from src.photos.db import (
    get_db_photos,
    create_db_photo,
    get_db_one_photo,
    update_db_photo,
    delete_db_photo
)

router = APIRouter(
    prefix="/photos",
    tags=["Photos"]
)

@router.get(
    "/", 
    status_code=200, 
    response_model=list[PhotoResponse],
    summary="Получить список фотографий",
    description="Возвращает список всех фотографий с возможностью пагинации"
)
async def get_photos(
    db: Session = Depends(get_db), 
    limit: int = 10, 
    offset: int = 0
):
    photos = get_db_photos(db, limit, offset)
    return photos

# Для фронтенда (JSON)
@router.post(
    "/json/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=PhotoResponse,
    summary="Создать новую фотографию (JSON)",
    description="Добавляет новую фотографию для набора или минифигурки (для фронтенда с JSON данными)"
)
async def create_photo(photo: PhotoCreate, db: Session = Depends(get_db)):
    new_photo = create_db_photo(photo, db)
    return new_photo

# Для /docs (форма)
@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=PhotoResponse,
    summary="Создать новую фотографию",
    description="Добавляет новую фотографию для набора или минифигурки"
)
async def create_photo_form(
    photo_url: str = Form(
        description="URL фотографии",
        example="https://example.com/images/hogwarts.jpg"
    ),
    set_id: int | None = Form(
        default=None,
        description="ID набора LEGO, к которому относится фото",
        example=75968
    ),
    minifigure_id: str | None = Form(
        default=None,
        description="ID минифигурки LEGO, к которой относится фото",
        example="hp150"
    ),
    is_main: bool = Form(
        default=False,
        description="Является ли фото основным для набора/минифигурки"
    ),
    db: Session = Depends(get_db)
):
    photo_data = PhotoCreate(
        photo_url=photo_url,
        set_id=set_id,
        minifigure_id=minifigure_id,
        is_main=is_main
    )
    new_photo = create_db_photo(photo_data, db)
    return new_photo

@router.get(
    "/{photo_id}", 
    status_code=200, 
    response_model=PhotoResponse,
    summary="Получить фотографию по ID",
    description="Возвращает информацию о конкретной фотографии по ее ID"
)
async def get_one_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = get_db_one_photo(db, photo_id)
    return photo

# Для фронтенда (JSON)
@router.put(
    "/{photo_id}/json/", 
    status_code=200, 
    response_model=PhotoResponse,
    summary="Обновить информацию о фотографии (JSON)",
    description="Обновляет информацию о фотографии по ее ID (для фронтенда с JSON данными)"
)
async def update_photo(photo_id: int, photo_update: PhotoUpdate, db: Session = Depends(get_db)):
    updated_photo = update_db_photo(photo_id, photo_update, db)
    return updated_photo

# Для /docs (форма)
@router.put(
    "/{photo_id}", 
    status_code=200, 
    response_model=PhotoResponse,
    summary="Обновить информацию о фотографии",
    description="Обновляет информацию о фотографии по ее ID"
)
async def update_photo_form(
    photo_id: int,
    photo_url: str | None = Form(
        default=None,
        description="URL фотографии",
        example="https://example.com/images/hogwarts.jpg"
    ),
    set_id: int | None = Form(
        default=None,
        description="ID набора LEGO, к которому относится фото",
        example=75968
    ),
    minifigure_id: str | None = Form(
        default=None,
        description="ID минифигурки LEGO, к которой относится фото",
        example="hp150"
    ),
    is_main: bool | None = Form(
        default=None,
        description="Является ли фото основным для набора/минифигурки"
    ),
    db: Session = Depends(get_db)
):
    photo_data = PhotoUpdate(
        photo_url=photo_url,
        set_id=set_id,
        minifigure_id=minifigure_id,
        is_main=is_main
    )
    updated_photo = update_db_photo(photo_id, photo_data, db)
    return updated_photo

# Для фронтенда (JSON)
@router.delete(
    "/json/", 
    status_code=200,
    summary="Удалить фотографию (JSON)",
    description="Удаляет фотографию по ее ID (для фронтенда с JSON данными)"
)
async def delete_photo(photo_delete: PhotoDelete, db: Session = Depends(get_db)):
    result = delete_db_photo(photo_delete, db)
    return result

# Для /docs (форма)
@router.delete(
    "/", 
    status_code=200,
    summary="Удалить фотографию",
    description="Удаляет фотографию по ее ID"
)
async def delete_photo_form(
    photo_id: int = Form(
        description="Уникальный идентификатор фотографии для удаления"
    ),
    db: Session = Depends(get_db)
):
    photo_delete = PhotoDelete(photo_id=photo_id)
    result = delete_db_photo(photo_delete, db)
    return result