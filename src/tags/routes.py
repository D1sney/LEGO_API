# src/tags/routes.py
from fastapi import status, HTTPException, Depends, APIRouter, Form
from sqlalchemy.orm import Session
from typing import Literal
from src.tags.schemas import TagCreate, TagResponse, TagUpdate, TagDelete, SetTagCreate, SetTagResponse, SetTagDelete, MinifigureTagCreate, MinifigureTagResponse, MinifigureTagDelete
from src.database import get_db
from src.tags.db import (
    get_db_tags,
    create_db_tag,
    get_db_one_tag,
    update_db_tag,
    delete_db_tag,
    create_db_set_tag,
    delete_db_set_tag,
    create_db_minifigure_tag,
    delete_db_minifigure_tag
)

router = APIRouter(
    prefix="/tags",
    tags=["Tags"]
)

@router.get(
    "/", 
    status_code=200, 
    response_model=list[TagResponse],
    summary="Получить список тегов",
    description="Возвращает список всех тегов с возможностью пагинации и поиска"
)
async def get_tags(
    db: Session = Depends(get_db), 
    limit: int = 10, 
    offset: int = 0, 
    search: str | None = ""
):
    tags = get_db_tags(db, limit, offset, search)
    return tags

# Для фронтенда (JSON)
@router.post(
    "/json/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=TagResponse,
    summary="Создать новый тег (JSON)",
    description="Создает новый тег в коллекции (для фронтенда с JSON данными)"
)
async def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    new_tag = create_db_tag(tag, db)
    return new_tag

# Для /docs (форма)
@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=TagResponse,
    summary="Создать новый тег",
    description="Создает новый тег в коллекции"
)
async def create_tag_form(
    name: str = Form(
        default="Хогвартс",
        description="Название тега"
    ),
    tag_type: Literal["set", "minifigure", "both"] = Form(
        default="both",
        description="Тип тега: set - только для наборов, minifigure - только для минифигурок, both - для обоих"
    ),
    db: Session = Depends(get_db)
):
    tag_data = TagCreate(
        name=name,
        tag_type=tag_type
    )
    new_tag = create_db_tag(tag_data, db)
    return new_tag

@router.get(
    "/{tag_id}", 
    status_code=200, 
    response_model=TagResponse,
    summary="Получить тег по ID",
    description="Возвращает информацию о конкретном теге по его ID"
)
async def get_one_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = get_db_one_tag(db, tag_id)
    return tag

# Для фронтенда (JSON)
@router.put(
    "/{tag_id}/json/", 
    status_code=200, 
    response_model=TagResponse,
    summary="Обновить информацию о теге (JSON)",
    description="Обновляет информацию о теге по его ID (для фронтенда с JSON данными)"
)
async def update_tag(tag_id: int, tag_update: TagUpdate, db: Session = Depends(get_db)):
    updated_tag = update_db_tag(tag_id, tag_update, db)
    return updated_tag

# Для /docs (форма)
@router.put(
    "/{tag_id}", 
    status_code=200, 
    response_model=TagResponse,
    summary="Обновить информацию о теге",
    description="Обновляет информацию о теге по его ID"
)
async def update_tag_form(
    tag_id: int,
    name: str | None = Form(
        default=None,
        description="Название тега",
        example="Хогвартс"
    ),
    tag_type: Literal["set", "minifigure", "both"] | None = Form(
        default=None,
        description="Тип тега: set - только для наборов, minifigure - только для минифигурок, both - для обоих",
        example="both"
    ),
    db: Session = Depends(get_db)
):
    tag_data = TagUpdate(
        name=name,
        tag_type=tag_type
    )
    updated_tag = update_db_tag(tag_id, tag_data, db)
    return updated_tag

# Для фронтенда (JSON)
@router.delete(
    "/json/", 
    status_code=200,
    summary="Удалить тег (JSON)",
    description="Удаляет тег из коллекции по его ID (для фронтенда с JSON данными)"
)
async def delete_tag(tag_delete: TagDelete, db: Session = Depends(get_db)):
    result = delete_db_tag(tag_delete, db)
    return result

# Для /docs (форма)
@router.delete(
    "/", 
    status_code=200,
    summary="Удалить тег",
    description="Удаляет тег из коллекции по его ID"
)
async def delete_tag_form(
    tag_id: int = Form(
        default=1,
        description="Уникальный идентификатор тега для удаления"
    ),
    db: Session = Depends(get_db)
):
    tag_delete = TagDelete(tag_id=tag_id)
    result = delete_db_tag(tag_delete, db)
    return result

# Эндпоинты для SetTag

# Для фронтенда (JSON)
@router.post(
    "/set-tags/json/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=SetTagResponse,
    summary="Добавить тег к набору (JSON)",
    description="Связывает тег с набором LEGO (для фронтенда с JSON данными)"
)
async def create_set_tag(set_tag: SetTagCreate, db: Session = Depends(get_db)):
    new_set_tag = create_db_set_tag(set_tag, db)
    return new_set_tag

# Для /docs (форма)
@router.post(
    "/set-tags/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=SetTagResponse,
    summary="Добавить тег к набору",
    description="Связывает тег с набором LEGO"
)
async def create_set_tag_form(
    set_id: int = Form(
        default=75968,
        description="ID набора LEGO"
    ),
    tag_id: int = Form(
        default=1,
        description="ID тега"
    ),
    db: Session = Depends(get_db)
):
    set_tag_data = SetTagCreate(
        set_id=set_id,
        tag_id=tag_id
    )
    new_set_tag = create_db_set_tag(set_tag_data, db)
    return new_set_tag

# Для фронтенда (JSON)
@router.delete(
    "/set-tags/json/", 
    status_code=200,
    summary="Удалить тег от набора (JSON)",
    description="Удаляет связь между тегом и набором LEGO (для фронтенда с JSON данными)"
)
async def delete_set_tag(set_tag_delete: SetTagDelete, db: Session = Depends(get_db)):
    result = delete_db_set_tag(set_tag_delete, db)
    return result

# Для /docs (форма)
@router.delete(
    "/set-tags/", 
    status_code=200,
    summary="Удалить тег от набора",
    description="Удаляет связь между тегом и набором LEGO"
)
async def delete_set_tag_form(
    set_id: int = Form(
        default=75968,
        description="ID набора LEGO"
    ),
    tag_id: int = Form(
        default=1,
        description="ID тега"
    ),
    db: Session = Depends(get_db)
):
    set_tag_delete = SetTagDelete(
        set_id=set_id,
        tag_id=tag_id
    )
    result = delete_db_set_tag(set_tag_delete, db)
    return result

# Эндпоинты для MinifigureTag

# Для фронтенда (JSON)
@router.post(
    "/minifigure-tags/json/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MinifigureTagResponse,
    summary="Добавить тег к минифигурке (JSON)",
    description="Связывает тег с минифигуркой LEGO (для фронтенда с JSON данными)"
)
async def create_minifigure_tag(minifigure_tag: MinifigureTagCreate, db: Session = Depends(get_db)):
    new_minifigure_tag = create_db_minifigure_tag(minifigure_tag, db)
    return new_minifigure_tag

# Для /docs (форма)
@router.post(
    "/minifigure-tags/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=MinifigureTagResponse,
    summary="Добавить тег к минифигурке",
    description="Связывает тег с минифигуркой LEGO"
)
async def create_minifigure_tag_form(
    minifigure_id: str = Form(
        default="hp150",
        description="ID минифигурки LEGO"
    ),
    tag_id: int = Form(
        default=1,
        description="ID тега"
    ),
    db: Session = Depends(get_db)
):
    minifigure_tag_data = MinifigureTagCreate(
        minifigure_id=minifigure_id,
        tag_id=tag_id
    )
    new_minifigure_tag = create_db_minifigure_tag(minifigure_tag_data, db)
    return new_minifigure_tag

# Для фронтенда (JSON)
@router.delete(
    "/minifigure-tags/json/", 
    status_code=200,
    summary="Удалить тег от минифигурки (JSON)",
    description="Удаляет связь между тегом и минифигуркой LEGO (для фронтенда с JSON данными)"
)
async def delete_minifigure_tag(minifigure_tag_delete: MinifigureTagDelete, db: Session = Depends(get_db)):
    result = delete_db_minifigure_tag(minifigure_tag_delete, db)
    return result

# Для /docs (форма)
@router.delete(
    "/minifigure-tags/", 
    status_code=200,
    summary="Удалить тег от минифигурки",
    description="Удаляет связь между тегом и минифигуркой LEGO"
)
async def delete_minifigure_tag_form(
    minifigure_id: str = Form(
        default="hp150",
        description="ID минифигурки LEGO"
    ),
    tag_id: int = Form(
        default=1,
        description="ID тега"
    ),
    db: Session = Depends(get_db)
):
    minifigure_tag_delete = MinifigureTagDelete(
        minifigure_id=minifigure_id,
        tag_id=tag_id
    )
    result = delete_db_minifigure_tag(minifigure_tag_delete, db)
    return result