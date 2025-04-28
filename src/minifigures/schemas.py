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
    price: Optional[float] = Field(None, description="Цена минифигурки в рублях", example=499.99)
    face_photo_id: Optional[int] = Field(None, description="ID главного фото минифигурки")

class MinifigureCreate(MinifigureBase):
    pass

class MinifigureUpdate(BaseModel):
    character_name: Optional[str] = Field(None, description="Имя персонажа", example="Гарри Поттер")
    name: Optional[str] = Field(None, description="Название минифигурки", example="Harry Potter, Gryffindor Robe")
    price: Optional[float] = Field(None, description="Цена минифигурки в рублях", example=499.99, gt=0)
    face_photo_id: Optional[int] = Field(None, description="ID главного фото минифигурки")

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
    min_price: Optional[float] = Field(default=None, description="Минимальная цена минифигурки в рублях", ge=0)
    max_price: Optional[float] = Field(default=None, description="Максимальная цена минифигурки в рублях", ge=0)

    @field_validator("tag_logic")
    @classmethod
    def validate_tag_logic(cls, value):
        if value.upper() not in ["AND", "OR"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="tag_logic должен быть 'AND' или 'OR'"
            )
        return value.upper()

    @field_validator("min_price", "max_price")
    @classmethod
    def validate_non_negative(cls, value, field):
        if value is not None and value < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field.name} не может быть отрицательным"
            )
        return value

    @field_validator("max_price")
    @classmethod
    def validate_price_range(cls, value, values):
        min_price = values.data.get("min_price")
        if value is not None and min_price is not None and value < min_price:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="max_price не может быть меньше min_price"
            )
        return value