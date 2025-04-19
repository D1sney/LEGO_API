# src/sets/routes.py
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from src.sets.schemas import SetCreate, SetResponse, SetUpdate, SetDelete, SetMinifigureCreate, SetMinifigureResponse, SetMinifigureDelete
from src.database import get_db
from src.sets.db import (
    get_db_sets,
    create_db_set,
    get_db_one_set,
    update_db_set,
    delete_db_set,
    create_db_set_minifigure,
    delete_db_set_minifigure
)

router = APIRouter(
    prefix="/sets",
    tags=["Sets"]
)

@router.get("/", status_code=200, response_model=list[SetResponse])
async def get_sets(db: Session = Depends(get_db), limit: int = 10, offset: int = 0, search: str | None = ""):
    sets = get_db_sets(db, limit, offset, search)
    return sets

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SetResponse)
async def create_set(set: SetCreate, db: Session = Depends(get_db)):
    new_set = create_db_set(set, db)
    return new_set

@router.get("/{set_id}", status_code=200, response_model=SetResponse)
async def get_one_set(set_id: int, db: Session = Depends(get_db)):
    set = get_db_one_set(db, set_id)
    return set

@router.put("/{set_id}", status_code=200, response_model=SetResponse)
async def update_set(set_id: int, set_update: SetUpdate, db: Session = Depends(get_db)):
    updated_set = update_db_set(set_id, set_update, db)
    return updated_set

@router.delete("/", status_code=200)
async def delete_set(set_delete: SetDelete, db: Session = Depends(get_db)):
    result = delete_db_set(set_delete, db)
    return result

# Эндпоинты для SetMinifigure
@router.post("/minifigures/", status_code=status.HTTP_201_CREATED, response_model=SetMinifigureResponse)
async def create_set_minifigure(set_minifigure: SetMinifigureCreate, db: Session = Depends(get_db)):
    new_set_minifigure = create_db_set_minifigure(set_minifigure, db)
    return new_set_minifigure

@router.delete("/minifigures/", status_code=200)
async def delete_set_minifigure(set_minifigure_delete: SetMinifigureDelete, db: Session = Depends(get_db)):
    result = delete_db_set_minifigure(set_minifigure_delete, db)
    return result