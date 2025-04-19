# src/Photo/schemas.py
from pydantic import BaseModel
from typing import Optional

class PhotoBase(BaseModel):
    set_id: Optional[int] = None
    minifigure_id: Optional[str] = None
    photo_url: str
    is_main: bool = False

class PhotoCreate(PhotoBase):
    pass

class PhotoUpdate(BaseModel):
    set_id: Optional[int] = None
    minifigure_id: Optional[str] = None
    photo_url: Optional[str] = None
    is_main: Optional[bool] = None

class PhotoResponse(PhotoBase):
    photo_id: int

    class Config:
        from_attributes = True

class PhotoDelete(BaseModel):
    photo_id: int