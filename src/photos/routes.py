# src/photos/routes.py
from fastapi import status, HTTPException, Depends, APIRouter, Form, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import shutil
import os
from pathlib import Path
from src.photos.schemas import PhotoCreate, PhotoResponse, PhotoUpdate, PhotoDelete, PhotoUploadData
from src.database import get_db
from src.photos.db import (
    get_db_photos,
    create_db_photo,
    get_db_one_photo,
    update_db_photo,
    delete_db_photo
)
from src.photos.utils import save_uploaded_file
from src.users.utils import get_current_active_user
from src.logger import app_logger

router = APIRouter(
    prefix="/photos",
    tags=["Photos"],
    dependencies=[Depends(get_current_active_user)]
)


@router.post(
    "/upload/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=PhotoResponse,
    summary="Загрузить фотографию",
    description="Загружает фотографию на сервер и создает запись в базе данных"
)
async def upload_photo(
    file: UploadFile = File(...),
    data: PhotoUploadData = Depends(),
    db: Session = Depends(get_db)
):
    # Сохраняем файл и получаем относительный путь
    relative_path = await save_uploaded_file(file)
    
    # Создаем запись в БД
    photo_data = PhotoCreate(
        photo_url=relative_path,
        set_id=data.set_id,
        minifigure_id=data.minifigure_id,
        is_main=data.is_main
    )
    
    # Сохраняем в БД
    new_photo = create_db_photo(photo_data, db)
    app_logger.info(f"Загружено фото: {relative_path} (set_id={data.set_id}, minifigure_id={data.minifigure_id})")
    return new_photo

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
    app_logger.info(f"Получено {len(photos)} фото (limit={limit}, offset={offset})")
    return photos

@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=PhotoResponse,
    summary="Создать новую фотографию",
    description="Добавляет новую фотографию для набора или минифигурки"
)
async def create_photo(photo: PhotoCreate, db: Session = Depends(get_db)):
    new_photo = create_db_photo(photo, db)
    app_logger.info(f"Создано фото: {new_photo.photo_url} (ID: {new_photo.photo_id})")
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
    app_logger.info(f"Получено фото ID: {photo_id}")
    return photo

@router.put(
    "/{photo_id}/", 
    status_code=200, 
    response_model=PhotoResponse,
    summary="Обновить информацию о фотографии",
    description="Обновляет информацию о фотографии по ее ID"
)
async def update_photo(photo_id: int, photo_update: PhotoUpdate, db: Session = Depends(get_db)):
    updated_photo = update_db_photo(photo_id, photo_update, db)
    app_logger.info(f"Обновлено фото ID: {photo_id}")
    return updated_photo

@router.delete(
    "/", 
    status_code=200,
    summary="Удалить фотографию",
    description="Удаляет фотографию по ее ID"
)
async def delete_photo(photo_delete: PhotoDelete, db: Session = Depends(get_db)):
    result = delete_db_photo(photo_delete, db)
    app_logger.info(f"Удалено фото ID: {photo_delete.photo_id}")
    return result