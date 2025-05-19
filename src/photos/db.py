# src/photos/db.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation, ForeignKeyViolation, NotNullViolation, CheckViolation
from src.photos.models import Photo
from src.photos.schemas import PhotoCreate, PhotoUpdate, PhotoDelete
from src.logger import log_db_operation

@log_db_operation
def get_db_photos(db: Session, limit: int = 10, offset: int = 0) -> list[Photo]:
    photos = db.query(Photo).limit(limit).offset(offset).all()
    return photos

@log_db_operation
def create_db_photo(photo: PhotoCreate, db: Session) -> Photo:
    new_photo = Photo(**photo.dict())
    try:
        db.add(new_photo)
        db.commit()
        db.refresh(new_photo)
        return new_photo
    except IntegrityError as e:
        db.rollback()
        if isinstance(e.orig, UniqueViolation):
            raise HTTPException(status_code=400, detail="Check unique field failed")
        elif isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(status_code=400, detail="Foreign key constraint failed")
        elif isinstance(e.orig, NotNullViolation):
            raise HTTPException(status_code=400, detail="Field cannot be null")
        elif isinstance(e.orig, CheckViolation):
            raise HTTPException(status_code=400, detail="Check constraint failed")
        else:
            raise HTTPException(status_code=400, detail="Integrity error")

@log_db_operation
def get_db_one_photo(db: Session, photo_id: int) -> Photo:
    one_photo = db.query(Photo).filter(Photo.photo_id == photo_id).first()
    if not one_photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Photo with id {photo_id} was not found")
    return one_photo

@log_db_operation
def update_db_photo(photo_id: int, photo_update: PhotoUpdate, db: Session) -> Photo:
    db_photo = get_db_one_photo(db, photo_id)
    update_data = photo_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_photo, key, value)
    try:
        db.commit()
        db.refresh(db_photo)
        return db_photo
    except IntegrityError as e:
        db.rollback()
        if isinstance(e.orig, UniqueViolation):
            raise HTTPException(status_code=400, detail="Check unique field failed")
        elif isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(status_code=400, detail="Foreign key constraint failed")
        elif isinstance(e.orig, NotNullViolation):
            raise HTTPException(status_code=400, detail="Field cannot be null")
        elif isinstance(e.orig, CheckViolation):
            raise HTTPException(status_code=400, detail="Check constraint failed")
        else:
            raise HTTPException(status_code=400, detail="Integrity error")

@log_db_operation
def delete_db_photo(photo_delete: PhotoDelete, db: Session) -> dict:
    db_photo = get_db_one_photo(db, photo_delete.photo_id)
    db.delete(db_photo)
    db.commit()
    return {"message": f"Photo with id {photo_delete.photo_id} deleted successfully"}