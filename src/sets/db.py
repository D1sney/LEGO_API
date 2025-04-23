# src/sets/db.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation, ForeignKeyViolation, NotNullViolation, CheckViolation
from src.sets.models import Set, SetMinifigure
from src.photos.models import Photo
from src.sets.schemas import SetCreate, SetUpdate, SetDelete, SetMinifigureCreate, SetMinifigureDelete

def get_db_sets(db: Session, limit: int = 10, offset: int = 0, search: str | None = "") -> list[Set]:
    # Используем joinedload для загрузки связанных фотографий одним запросом
    sets = db.query(Set).options(joinedload(Set.face_photo)).filter(Set.name.contains(search)).limit(limit).offset(offset).all()
    return sets

def create_db_set(set: SetCreate, db: Session) -> Set:
    new_set = Set(**set.dict())
    try:
        db.add(new_set)
        db.commit()
        db.refresh(new_set)
        return db.query(Set).options(joinedload(Set.face_photo)).filter(Set.set_id == new_set.set_id).first()
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

def get_db_one_set(db: Session, set_id: int) -> Set:
    # Используем joinedload для загрузки связанных фотографий одним запросом
    one_set = db.query(Set).options(joinedload(Set.face_photo)).filter(Set.set_id == set_id).first()
    if not one_set:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Set with id {set_id} was not found")
    return one_set

def update_db_set(set_id: int, set_update: SetUpdate, db: Session) -> Set:
    db_set = get_db_one_set(db, set_id)
    update_data = set_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_set, key, value)
    try:
        db.commit()
        return db.query(Set).options(joinedload(Set.face_photo)).filter(Set.set_id == set_id).first()
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

def delete_db_set(set_delete: SetDelete, db: Session) -> dict:
    db_set = get_db_one_set(db, set_delete.set_id)
    db.delete(db_set)
    db.commit()
    return {"message": f"Set with id {set_delete.set_id} deleted successfully"}

# Операции для SetMinifigure
def create_db_set_minifigure(set_minifigure: SetMinifigureCreate, db: Session) -> SetMinifigure:
    new_set_minifigure = SetMinifigure(**set_minifigure.dict())
    try:
        db.add(new_set_minifigure)
        db.commit()
        db.refresh(new_set_minifigure)
        return new_set_minifigure
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

def delete_db_set_minifigure(set_minifigure_delete: SetMinifigureDelete, db: Session) -> dict:
    db_set_minifigure = db.query(SetMinifigure).filter(
        SetMinifigure.set_id == set_minifigure_delete.set_id,
        SetMinifigure.minifigure_id == set_minifigure_delete.minifigure_id
    ).first()
    if not db_set_minifigure:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SetMinifigure not found")
    db.delete(db_set_minifigure)
    db.commit()
    return {"message": f"SetMinifigure with set_id {set_minifigure_delete.set_id} and minifigure_id {set_minifigure_delete.minifigure_id} deleted successfully"}