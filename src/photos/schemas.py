# src/Photo/schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class PhotoBase(BaseModel):
    set_id: Optional[int] = Field(None, description="ID набора LEGO, к которому относится фото", example=75968)
    minifigure_id: Optional[str] = Field(None, description="ID минифигурки LEGO, к которой относится фото", example="hp150")
    photo_url: str = Field(..., description="URL фотографии", example="https://example.com/images/hogwarts.jpg")
    is_main: bool = Field(False, description="Является ли фото основным для набора/минифигурки")

class PhotoCreate(PhotoBase):
    pass

class PhotoUpdate(BaseModel):
    set_id: Optional[int] = Field(None, description="ID набора LEGO, к которому относится фото", example=75968)
    minifigure_id: Optional[str] = Field(None, description="ID минифигурки LEGO, к которой относится фото", example="hp150")
    photo_url: Optional[str] = Field(None, description="URL фотографии", example="https://example.com/images/hogwarts.jpg")
    is_main: Optional[bool] = Field(None, description="Является ли фото основным для набора/минифигурки")

class PhotoResponse(PhotoBase):
    photo_id: int = Field(..., description="Уникальный идентификатор фотографии")

    class Config:
        from_attributes = True

class PhotoDelete(BaseModel):
    photo_id: int = Field(..., description="Уникальный идентификатор фотографии для удаления")