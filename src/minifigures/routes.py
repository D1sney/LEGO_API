# src/minifigures/routes.py
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from src.minifigures.schemas import MinifigureCreate, MinifigureResponse, MinifigureUpdate, MinifigureDelete
from src.database import get_db
from src.minifigures.db import (
    get_db_minifigures,
    create_db_minifigure,
    get_db_one_minifigure,
    update_db_minifigure,
    delete_db_minifigure
)

router = APIRouter(
    prefix="/minifigures",
    tags=["Minifigures"]
)

@router.get("/", status_code=200, response_model=list[MinifigureResponse])
async def get_minifigures(db: Session = Depends(get_db), limit: int = 10, offset: int = 0, search: str | None = ""):
    minifigures = get_db_minifigures(db, limit, offset, search)
    return minifigures

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MinifigureResponse)
async def create_minifigure(minifigure: MinifigureCreate, db: Session = Depends(get_db)):
    new_minifigure = create_db_minifigure(minifigure, db)
    return new_minifigure

@router.get("/{minifigure_id}", status_code=200, response_model=MinifigureResponse)
async def get_one_minifigure(minifigure_id: str, db: Session = Depends(get_db)):
    minifigure = get_db_one_minifigure(db, minifigure_id)
    return minifigure

@router.put("/{minifigure_id}", status_code=200, response_model=MinifigureResponse)
async def update_minifigure(minifigure_id: str, minifigure_update: MinifigureUpdate, db: Session = Depends(get_db)):
    updated_minifigure = update_db_minifigure(minifigure_id, minifigure_update, db)
    return updated_minifigure

@router.delete("/", status_code=200)
async def delete_minifigure(minifigure_delete: MinifigureDelete, db: Session = Depends(get_db)):
    result = delete_db_minifigure(minifigure_delete, db)
    return result