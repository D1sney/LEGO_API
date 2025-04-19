# src/tags/routes.py
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
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

@router.get("/", status_code=200, response_model=list[TagResponse])
async def get_tags(db: Session = Depends(get_db), limit: int = 10, offset: int = 0, search: str | None = ""):
    tags = get_db_tags(db, limit, offset, search)
    return tags

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TagResponse)
async def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    new_tag = create_db_tag(tag, db)
    return new_tag

@router.get("/{tag_id}", status_code=200, response_model=TagResponse)
async def get_one_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = get_db_one_tag(db, tag_id)
    return tag

@router.put("/{tag_id}", status_code=200, response_model=TagResponse)
async def update_tag(tag_id: int, tag_update: TagUpdate, db: Session = Depends(get_db)):
    updated_tag = update_db_tag(tag_id, tag_update, db)
    return updated_tag

@router.delete("/", status_code=200)
async def delete_tag(tag_delete: TagDelete, db: Session = Depends(get_db)):
    result = delete_db_tag(tag_delete, db)
    return result

# Эндпоинты для SetTag
@router.post("/set-tags/", status_code=status.HTTP_201_CREATED, response_model=SetTagResponse)
async def create_set_tag(set_tag: SetTagCreate, db: Session = Depends(get_db)):
    new_set_tag = create_db_set_tag(set_tag, db)
    return new_set_tag

@router.delete("/set-tags/", status_code=200)
async def delete_set_tag(set_tag_delete: SetTagDelete, db: Session = Depends(get_db)):
    result = delete_db_set_tag(set_tag_delete, db)
    return result

# Эндпоинты для MinifigureTag
@router.post("/minifigure-tags/", status_code=status.HTTP_201_CREATED, response_model=MinifigureTagResponse)
async def create_minifigure_tag(minifigure_tag: MinifigureTagCreate, db: Session = Depends(get_db)):
    new_minifigure_tag = create_db_minifigure_tag(minifigure_tag, db)
    return new_minifigure_tag

@router.delete("/minifigure-tags/", status_code=200)
async def delete_minifigure_tag(minifigure_tag_delete: MinifigureTagDelete, db: Session = Depends(get_db)):
    result = delete_db_minifigure_tag(minifigure_tag_delete, db)
    return result