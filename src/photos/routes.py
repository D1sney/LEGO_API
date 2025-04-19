# src/photos/routes.py
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from src.photos.schemas import PhotosCreate, PhotosResponse, PhotosUpdate, PhotosDelete
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

@router.get("/", status_code=200, response_model=list[PhotosResponse])
async def get_photos(db: Session = Depends(get_db), limit: int = 10, offset: int = 0):
    photos = get_db_photos(db, limit, offset)
    return photos

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PhotosResponse)
async def create_photo(photo: PhotosCreate, db: Session = Depends(get_db)):
    new_photo = create_db_photo(photo, db)
    return new_photo

@router.get("/{photo_id}", status_code=200, response_model=PhotosResponse)
async def get_one_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = get_db_one_photo(db, photo_id)
    return photo

@router.put("/{photo_id}", status_code=200, response_model=PhotosResponse)
async def update_photo(photo_id: int, photo_update: PhotosUpdate, db: Session = Depends(get_db)):
    updated_photo = update_db_photo(photo_id, photo_update, db)
    return updated_photo

@router.delete("/", status_code=200)
async def delete_photo(photo_delete: PhotosDelete, db: Session = Depends(get_db)):
    result = delete_db_photo(photo_delete, db)
    return result