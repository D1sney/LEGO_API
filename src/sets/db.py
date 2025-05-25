# src/sets/db.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation, ForeignKeyViolation, NotNullViolation, CheckViolation
from src.sets.models import Set, SetMinifigure
from src.photos.models import Photo
from src.tags.models import Tag, SetTag
from src.sets.schemas import SetCreate, SetUpdate, SetDelete, SetMinifigureCreate, SetMinifigureDelete
from typing import Optional, List
from sqlalchemy.sql import func
from sqlalchemy import distinct, case
from src.logger import log_db_operation

@log_db_operation
def get_db_sets(db: Session, limit: int = 10, offset: int = 0, search: str = "", tag_names: Optional[str] = "", tag_logic: str = "AND", min_price: Optional[float] = None, max_price: Optional[float] = None, min_piece_count: Optional[int] = None, max_piece_count: Optional[int] = None) -> list[Set]:
    # Формируем базовый запрос с загрузкой связанных данных
    query = db.query(Set).options(
        joinedload(Set.face_photo),
        joinedload(Set.tags),
        # Загружаем все фотографии без предварительной сортировки в SQL
        joinedload(Set.photos)
    ).filter(Set.name.contains(search))

    # Применяем фильтрацию по цене
    if min_price is not None:
        query = query.filter(Set.price >= min_price)
    if max_price is not None:
        query = query.filter(Set.price <= max_price)

    # Применяем фильтрацию по количеству деталей
    if min_piece_count is not None:
        query = query.filter(Set.piece_count >= min_piece_count)
    if max_piece_count is not None:
        query = query.filter(Set.piece_count <= max_piece_count)

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
        query = query.join(SetTag, Set.set_id == SetTag.set_id)\
                     .join(Tag, SetTag.tag_id == Tag.tag_id)\
                     .filter(Tag.name.in_(tags_list))
        if tag_logic == "AND":
            # Для AND возвращаем только наборы, содержащие все указанные теги
            query = query.group_by(Set.set_id)\
                         .having(func.count(distinct(Tag.name)) == len(tags_list))
        # Для OR не используем having, что возвращает наборы с хотя бы одним тегом

    # Применяем пагинацию
    sets = query.limit(limit).offset(offset).all()
    
    # Сортируем фотографии для каждого набора, чтобы главная фотография была первой
    for set_item in sets:
        set_item.photos = sorted(set_item.photos, key=lambda photo: 0 if photo.is_main else 1)
    
    return sets

@log_db_operation
def create_db_set(set: SetCreate, db: Session) -> Set:
    new_set = Set(**set.dict())
    try:
        db.add(new_set)
        db.commit()
        db.refresh(new_set)
        return db.query(Set).options(joinedload(Set.face_photo), joinedload(Set.photos)).filter(Set.set_id == new_set.set_id).first()
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
def get_db_one_set(db: Session, set_id: int) -> Set:
    # Используем joinedload для загрузки связанных фотографий и тегов одним запросом
    one_set = db.query(Set).options(
        joinedload(Set.face_photo),
        joinedload(Set.tags),
        # Загружаем все фотографии без предварительной сортировки в SQL
        joinedload(Set.photos)
    ).filter(Set.set_id == set_id).first()
    
    if not one_set:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Set with id {set_id} was not found")
    
    # Сортируем фотографии, чтобы главная фотография была первой
    one_set.photos = sorted(one_set.photos, key=lambda photo: 0 if photo.is_main else 1)
    
    return one_set

@log_db_operation
def update_db_set(set_id: int, set_update: SetUpdate, db: Session) -> Set:
    db_set = get_db_one_set(db, set_id)
    update_data = set_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_set, key, value)
    try:
        db.commit()
        return db.query(Set).options(joinedload(Set.face_photo), joinedload(Set.photos)).filter(Set.set_id == set_id).first()
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
def delete_db_set(set_delete: SetDelete, db: Session) -> dict:
    db_set = get_db_one_set(db, set_delete.set_id)
    db.delete(db_set)
    db.commit()
    return {"message": f"Set with id {set_delete.set_id} deleted successfully"}

# Операции для SetMinifigure
@log_db_operation
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

@log_db_operation
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