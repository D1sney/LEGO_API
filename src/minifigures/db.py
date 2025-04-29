# src/minifigures/db.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation, ForeignKeyViolation, NotNullViolation, CheckViolation
from src.minifigures.models import Minifigure
from src.photos.models import Photo
from src.tags.models import Tag, MinifigureTag
from src.minifigures.schemas import MinifigureCreate, MinifigureUpdate, MinifigureDelete
from typing import Optional, List
from sqlalchemy.sql import func
from sqlalchemy import distinct

def get_db_minifigures(db: Session, limit: int = 10, offset: int = 0, search: str = "", tag_names: Optional[str] = "", tag_logic: str = "AND", min_price: Optional[float] = None, max_price: Optional[float] = None) -> list[Minifigure]:
    # Формируем базовый запрос с загрузкой связанных данных
    query = db.query(Minifigure).options(
        joinedload(Minifigure.face_photo),
        joinedload(Minifigure.photos),
        joinedload(Minifigure.tags)
    ).filter(Minifigure.name.contains(search))

    # Применяем фильтрацию по цене
    if min_price is not None:
        query = query.filter(Minifigure.price >= min_price)
    if max_price is not None:
        query = query.filter(Minifigure.price <= max_price)

    # Обрабатываем фильтрацию по тегам
    tags_list = []
    if tag_names:
        tags_list = [tag.strip() for tag in tag_names.split(",") if tag.strip()]
        # Удаляем дубликаты из списка тегов
        tags_list = list(set(tags_list))
        
        # Проверяем существование всех тегов
        non_existent_tags = []
        for tag_name in tags_list:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                non_existent_tags.append(tag_name)
        if non_existent_tags:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Теги с именами {', '.join(non_existent_tags)} не найдены"
            )
        
        # Применяем фильтрацию по тегам
        query = query.join(MinifigureTag, Minifigure.minifigure_id == MinifigureTag.minifigure_id)\
                     .join(Tag, MinifigureTag.tag_id == Tag.tag_id)\
                     .filter(Tag.name.in_(tags_list))
        if tag_logic == "AND":
            # Для AND возвращаем только минифигурки, содержащие все указанные теги
            query = query.group_by(Minifigure.minifigure_id)\
                         .having(func.count(distinct(Tag.name)) == len(tags_list))
        # Для OR не используем having, что возвращает минифигурки с хотя бы одним тегом

    # Применяем пагинацию
    minifigures = query.limit(limit).offset(offset).all()
    
    # Сортируем фотографии для каждой минифигурки, чтобы главная фотография была первой
    for minifigure in minifigures:
        minifigure.photos = sorted(minifigure.photos, key=lambda photo: 0 if photo.is_main else 1)
    
    return minifigures

def create_db_minifigure(minifigure: MinifigureCreate, db: Session) -> Minifigure:
    new_minifigure = Minifigure(**minifigure.dict())
    try:
        db.add(new_minifigure)
        db.commit()
        db.refresh(new_minifigure)
        return db.query(Minifigure).options(joinedload(Minifigure.face_photo), joinedload(Minifigure.photos)).filter(Minifigure.minifigure_id == new_minifigure.minifigure_id).first()
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
    one_minifigure = db.query(Minifigure).options(
        joinedload(Minifigure.face_photo),
        joinedload(Minifigure.photos),
        joinedload(Minifigure.tags)
    ).filter(Minifigure.minifigure_id == minifigure_id).first()
    if not one_minifigure:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Minifigure with id {minifigure_id} was not found")
    
    # Сортируем фотографии, чтобы главная фотография была первой
    one_minifigure.photos = sorted(one_minifigure.photos, key=lambda photo: 0 if photo.is_main else 1)
    
    return one_minifigure

def update_db_minifigure(minifigure_id: str, minifigure_update: MinifigureUpdate, db: Session) -> Minifigure:
    db_minifigure = get_db_one_minifigure(db, minifigure_id)
    update_data = minifigure_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_minifigure, key, value)
    try:
        db.commit()
        return db.query(Minifigure).options(joinedload(Minifigure.face_photo), joinedload(Minifigure.photos)).filter(Minifigure.minifigure_id == minifigure_id).first()
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