# src/Photo/schemas.py
from pydantic import BaseModel, Field, field_validator
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

    @field_validator("photo_url", mode="before")
    @classmethod
    def make_absolute_url(cls, value):
        # Преобразуем относительный путь в абсолютный URL
        base_url = "http://127.0.0.1:8000"  # Замени на адрес твоего сервера при деплое
        return f"{base_url}/static/{value}"
    
    class Config:
        from_attributes = True

class PhotoDelete(BaseModel):
    photo_id: int = Field(..., description="Уникальный идентификатор фотографии для удаления")

class PhotoUploadData(BaseModel):
    set_id: Optional[int] = Field(None, description="ID набора LEGO (оставьте пустым если не связано с набором)")
    minifigure_id: Optional[str] = Field(None, description="ID минифигурки LEGO (оставьте пустым если не связано с минифигуркой)")
    is_main: bool = Field(False, description="Является ли фото основным")