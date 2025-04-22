# src/minifigures/db.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation, ForeignKeyViolation, NotNullViolation, CheckViolation
from src.minifigures.models import Minifigure
from src.photos.models import Photo
from src.minifigures.schemas import MinifigureCreate, MinifigureUpdate, MinifigureDelete

def get_db_minifigures(db: Session, limit: int = 10, offset: int = 0, search: str | None = "") -> list[Minifigure]:
    minifigures = db.query(Minifigure).options(joinedload(Minifigure.face_photo)).filter(Minifigure.name.contains(search)).limit(limit).offset(offset).all()
    return minifigures

def create_db_minifigure(minifigure: MinifigureCreate, db: Session) -> Minifigure:
    new_minifigure = Minifigure(**minifigure.dict())
    try:
        db.add(new_minifigure)
        db.commit()
        db.refresh(new_minifigure)
        if new_minifigure.face_photo_id:
            db.refresh(new_minifigure, ['face_photo'])
        return new_minifigure
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

def get_db_one_minifigure(db: Session, minifigure_id: str) -> Minifigure:
    one_minifigure = db.query(Minifigure).options(joinedload(Minifigure.face_photo)).filter(Minifigure.minifigure_id == minifigure_id).first()
    if not one_minifigure:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Minifigure with id {minifigure_id} was not found")
    return one_minifigure

def update_db_minifigure(minifigure_id: str, minifigure_update: MinifigureUpdate, db: Session) -> Minifigure:
    db_minifigure = get_db_one_minifigure(db, minifigure_id)
    update_data = minifigure_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_minifigure, key, value)
    try:
        db.commit()
        db.refresh(db_minifigure)
        if db_minifigure.face_photo_id:
            db.refresh(db_minifigure, ['face_photo'])
        return db_minifigure
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

def delete_db_minifigure(minifigure_delete: MinifigureDelete, db: Session) -> dict:
    db_minifigure = get_db_one_minifigure(db, minifigure_delete.minifigure_id)
    db.delete(db_minifigure)
    db.commit()
    return {"message": f"Minifigure with id {minifigure_delete.minifigure_id} deleted successfully"}