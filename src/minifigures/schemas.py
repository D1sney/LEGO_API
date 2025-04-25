# src/minifigures/schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from src.photos.schemas import PhotoResponse
from src.tags.schemas import TagResponse

class MinifigureBase(BaseModel):
    minifigure_id: str = Field(..., description="Уникальный идентификатор минифигурки (например, hp150)", example="hp150")
    character_name: str = Field(..., description="Имя персонажа", example="Гарри Поттер")
    name: str = Field(..., description="Название минифигурки", example="Harry Potter, Gryffindor Robe")
    face_photo_id: Optional[int] = Field(None, description="ID главного фото минифигурки")

class MinifigureCreate(MinifigureBase):
    @field_validator("face_photo_id", mode="before")
    @classmethod
    def parse_face_photo_id(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        try:
            return int(value) if value is not None else None
        except (ValueError, TypeError):
            raise ValueError("face_photo_id должен быть целым числом или пустым")

class MinifigureUpdate(BaseModel):
    character_name: Optional[str] = Field(None, description="Имя персонажа", example="Гарри Поттер")
    name: Optional[str] = Field(None, description="Название минифигурки", example="Harry Potter, Gryffindor Robe")
    face_photo_id: Optional[int] = Field(None, description="ID главного фото минифигурки")
    
    @field_validator("face_photo_id", mode="before")
    @classmethod
    def parse_face_photo_id(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        try:
            return int(value) if value is not None else None
        except (ValueError, TypeError):
            raise ValueError("face_photo_id должен быть целым числом или пустым")

class MinifigureResponse(MinifigureBase):
    face_photo: Optional[PhotoResponse] = Field(None, description="Информация о главной фотографии минифигурки")
    tags: List[TagResponse] = Field(default=[], description="Список тегов, связанных с минифигуркой")
    
    class Config:
        from_attributes = True

class MinifigureDelete(BaseModel):
    minifigure_id: str = Field(..., description="Уникальный идентификатор минифигурки для удаления", example="hp150")

class MinifigureFilter(BaseModel):
    limit: int = Field(default=10, description="Количество возвращаемых записей", ge=1, le=1000)
    offset: int = Field(default=0, description="Смещение для пагинации", ge=0)
    search: Optional[str] = Field(default="", description="Поиск по названию минифигурки")
    tag_names: Optional[str] = Field(default="", description="Список имен тегов, разделённых запятыми, для фильтрации минифигурок")
    tag_logic: Optional[str] = Field(default="AND", description="Логика фильтрации тегов: AND или OR")

    @field_validator("tag_logic")
    @classmethod
    def validate_tag_logic(cls, value):
        if value.upper() not in ["AND", "OR"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="tag_logic должен быть 'AND' или 'OR'"
            )
        return value.upper()