# src/sets/schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from src.photos.schemas import PhotoResponse

class SetBase(BaseModel):
    name: str = Field(..., description="Название набора LEGO", example="Хогвартс: Астрономическая башня")
    piece_count: int = Field(..., description="Количество деталей в наборе", example=971, gt=0)
    release_year: int = Field(..., description="Год выпуска набора", example=2020, ge=1949)
    theme: str = Field(..., description="Основная тема набора", example="Harry Potter")
    sub_theme: Optional[str] = Field(None, description="Подтема набора (если есть)", example="Hogwarts")
    price: float = Field(..., description="Цена набора в рублях", example=8999.99, gt=0)
    face_photo_id: Optional[int] = Field(None, description="ID главного фото набора")

class SetCreate(SetBase):
    @field_validator("face_photo_id", mode="before")
    @classmethod
    def parse_face_photo_id(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        try:
            return int(value) if value is not None else None
        except (ValueError, TypeError):
            raise ValueError("face_photo_id должен быть целым числом или пустым")
    
    @field_validator("sub_theme", mode="before")
    @classmethod
    def parse_sub_theme(cls, value):
        # Превращаем пустую строку в None
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        return value

class SetUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Название набора LEGO", example="Хогвартс: Астрономическая башня")
    piece_count: Optional[int] = Field(None, description="Количество деталей в наборе", example=971, gt=0)
    release_year: Optional[int] = Field(None, description="Год выпуска набора", example=2020, ge=1949)
    theme: Optional[str] = Field(None, description="Основная тема набора", example="Harry Potter")
    sub_theme: Optional[str] = Field(None, description="Подтема набора (если есть)", example="Hogwarts")
    price: Optional[float] = Field(None, description="Цена набора в рублях", example=8999.99, gt=0)
    face_photo_id: Optional[int] = Field(None, description="ID главного фото набора")
    
    @field_validator("face_photo_id", mode="before")
    @classmethod
    def parse_face_photo_id(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        try:
            return int(value) if value is not None else None
        except (ValueError, TypeError):
            raise ValueError("face_photo_id должен быть целым числом или пустым")
    
    @field_validator("sub_theme", mode="before")
    @classmethod
    def parse_sub_theme(cls, value):
        # Превращаем пустую строку в None
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        return value

class SetResponse(SetBase):
    set_id: int = Field(..., description="Уникальный идентификатор набора")
    face_photo: Optional[PhotoResponse] = Field(None, description="Информация о главной фотографии набора")

    class Config:
        from_attributes = True

class SetDelete(BaseModel):
    set_id: int = Field(..., description="Уникальный идентификатор набора для удаления")


# Связи Наборов и Минифигурок
class SetMinifigureBase(BaseModel):
    set_id: int = Field(..., description="ID набора LEGO")
    minifigure_id: str = Field(..., description="ID минифигурки LEGO")

class SetMinifigureCreate(SetMinifigureBase):
    pass

class SetMinifigureUpdate(BaseModel):
    set_id: Optional[int] = Field(None, description="ID набора LEGO")
    minifigure_id: Optional[str] = Field(None, description="ID минифигурки LEGO")

class SetMinifigureResponse(SetMinifigureBase):
    class Config:
        from_attributes = True

class SetMinifigureDelete(BaseModel):
    set_id: int = Field(..., description="ID набора LEGO для удаления связи")
    minifigure_id: str = Field(..., description="ID минифигурки LEGO для удаления связи")