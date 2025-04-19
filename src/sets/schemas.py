# src/sets/schemas.py
from pydantic import BaseModel
from typing import Optional

class SetBase(BaseModel):
    name: str
    piece_count: int
    release_year: int
    theme: str
    sub_theme: Optional[str] = None
    price: float
    face_photo_id: Optional[int] = None

class SetCreate(SetBase):
    pass

class SetUpdate(BaseModel):
    name: Optional[str] = None
    piece_count: Optional[int] = None
    release_year: Optional[int] = None
    theme: Optional[str] = None
    sub_theme: Optional[str] = None
    price: Optional[float] = None
    face_photo_id: Optional[int] = None

class SetResponse(SetBase):
    set_id: int

    class Config:
        from_attributes = True

class SetDelete(BaseModel):
    set_id: int


# Связи Наборов и Минифигурок
class SetMinifigureBase(BaseModel):
    set_id: int
    minifigure_id: str

class SetMinifigureCreate(SetMinifigureBase):
    pass

class SetMinifigureUpdate(BaseModel):
    set_id: Optional[int] = None
    minifigure_id: Optional[str] = None

class SetMinifigureResponse(SetMinifigureBase):
    class Config:
        from_attributes = True

class SetMinifigureDelete(BaseModel):
    set_id: int
    minifigure_id: str