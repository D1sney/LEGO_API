# src/tags/db.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation, ForeignKeyViolation, NotNullViolation, CheckViolation
from src.tags.models import Tag, SetTag, MinifigureTag
from src.tags.schemas import TagCreate, TagUpdate, TagDelete, SetTagCreate, SetTagDelete, MinifigureTagCreate, MinifigureTagDelete
from src.logger import log_db_operation

@log_db_operation
def get_db_tags(db: Session, limit: int = 10, offset: int = 0, search: str | None = "") -> list[Tag]:
    tags = db.query(Tag).filter(Tag.name.contains(search)).limit(limit).offset(offset).all()
    return tags

@log_db_operation
def create_db_tag(tag: TagCreate, db: Session) -> Tag:
    new_tag = Tag(**tag.dict())
    try:
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        return new_tag
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
def get_db_one_tag(db: Session, tag_id: int) -> Tag:
    one_tag = db.query(Tag).filter(Tag.tag_id == tag_id).first()
    if not one_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag with id {tag_id} was not found")
    return one_tag

@log_db_operation
def update_db_tag(tag_id: int, tag_update: TagUpdate, db: Session) -> Tag:
    db_tag = get_db_one_tag(db, tag_id)
    update_data = tag_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tag, key, value)
    try:
        db.commit()
        db.refresh(db_tag)
        return db_tag
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
def delete_db_tag(tag_delete: TagDelete, db: Session) -> dict:
    db_tag = get_db_one_tag(db, tag_delete.tag_id)
    db.delete(db_tag)
    db.commit()
    return {"message": f"Tag with id {tag_delete.tag_id} deleted successfully"}

# Операции для SetTag
@log_db_operation
def create_db_set_tag(set_tag: SetTagCreate, db: Session) -> SetTag:
    new_set_tag = SetTag(**set_tag.dict())
    try:
        db.add(new_set_tag)
        db.commit()
        db.refresh(new_set_tag)
        return new_set_tag
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
def delete_db_set_tag(set_tag_delete: SetTagDelete, db: Session) -> dict:
    db_set_tag = db.query(SetTag).filter(
        SetTag.set_id == set_tag_delete.set_id,
        SetTag.tag_id == set_tag_delete.tag_id
    ).first()
    if not db_set_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SetTag not found")
    db.delete(db_set_tag)
    db.commit()
    return {"message": f"SetTag with set_id {set_tag_delete.set_id} and tag_id {set_tag_delete.tag_id} deleted successfully"}

# Операции для MinifigureTag
@log_db_operation
def create_db_minifigure_tag(minifigure_tag: MinifigureTagCreate, db: Session) -> MinifigureTag:
    new_minifigure_tag = MinifigureTag(**minifigure_tag.dict())
    try:
        db.add(new_minifigure_tag)
        db.commit()
        db.refresh(new_minifigure_tag)
        return new_minifigure_tag
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
def delete_db_minifigure_tag(minifigure_tag_delete: MinifigureTagDelete, db: Session) -> dict:
    db_minifigure_tag = db.query(MinifigureTag).filter(
        MinifigureTag.minifigure_id == minifigure_tag_delete.minifigure_id,
        MinifigureTag.tag_id == minifigure_tag_delete.tag_id
    ).first()
    if not db_minifigure_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MinifigureTag not found")
    db.delete(db_minifigure_tag)
    db.commit()
    return {"message": f"MinifigureTag with minifigure_id {minifigure_tag_delete.minifigure_id} and tag_id {minifigure_tag_delete.tag_id} deleted successfully"}