# src/minifigures/schemas.py
from pydantic import BaseModel
from typing import Optional

class MinifigureBase(BaseModel):
    minifigure_id: str
    character_name: str
    name: str
    face_photo_id: Optional[int] = None

class MinifigureCreate(MinifigureBase):
    pass

class MinifigureUpdate(BaseModel):
    character_name: Optional[str] = None
    name: Optional[str] = None
    face_photo_id: Optional[int] = None

class MinifigureResponse(MinifigureBase):
    class Config:
        from_attributes = True

class MinifigureDelete(BaseModel):
    minifigure_id: str