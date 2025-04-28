# src/sets/schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from src.photos.schemas import PhotoResponse
from src.tags.schemas import TagResponse
from fastapi import Query, HTTPException, status

class SetBase(BaseModel):
    name: str = Field(..., description="Название набора LEGO", example="Хогвартс: Астрономическая башня")
    piece_count: int = Field(..., description="Количество деталей в наборе", example=971, gt=0)
    release_year: int = Field(..., description="Год выпуска набора", example=2020, ge=1949)
    theme: str = Field(..., description="Основная тема набора", example="Harry Potter")
    sub_theme: Optional[str] = Field(None, description="Подтема набора (если есть)", example="Hogwarts")
    price: float = Field(..., description="Цена набора в рублях", example=8999.99, gt=0)
    face_photo_id: Optional[int] = Field(None, description="ID главного фото набора")

class SetCreate(SetBase):
    pass

class SetUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Название набора LEGO", example="Хогвартс: Астрономическая башня")
    piece_count: Optional[int] = Field(None, description="Количество деталей в наборе", example=971, gt=0)
    release_year: Optional[int] = Field(None, description="Год выпуска набора", example=2020, ge=1949)
    theme: Optional[str] = Field(None, description="Основная тема набора", example="Harry Potter")
    sub_theme: Optional[str] = Field(None, description="Подтема набора (если есть)", example="Hogwarts")
    price: Optional[float] = Field(None, description="Цена набора в рублях", example=8999.99, gt=0)
    face_photo_id: Optional[int] = Field(None, description="ID главного фото набора")

class SetResponse(SetBase):
    set_id: int = Field(..., description="Уникальный идентификатор набора")
    face_photo: Optional[PhotoResponse] = Field(None, description="Информация о главной фотографии набора")
    tags: List[TagResponse] = Field(default=[], description="Список тегов, связанных с набором")

    class Config:
        from_attributes = True

class SetDelete(BaseModel):
    set_id: int = Field(..., description="Уникальный идентификатор набора для удаления")


class SetFilter(BaseModel):
    limit: int = Field(default=10, description="Количество возвращаемых записей", ge=1, le=1000)
    offset: int = Field(default=0, description="Смещение для пагинации", ge=0)
    search: Optional[str] = Field(default="", description="Поиск по названию набора")
    tag_names: Optional[str] = Field(default="", description="Список имен тегов, разделённых запятыми, для фильтрации наборов")
    tag_logic: Optional[str] = Field(default="AND", description="Логика фильтрации тегов: AND или OR")
    min_price: Optional[float] = Field(default=None, description="Минимальная цена набора в рублях", ge=0)
    max_price: Optional[float] = Field(default=None, description="Максимальная цена набора в рублях", ge=0)
    min_piece_count: Optional[int] = Field(default=None, description="Минимальное количество деталей в наборе", ge=0)
    max_piece_count: Optional[int] = Field(default=None, description="Максимальное количество деталей в наборе", ge=0)

    @field_validator("tag_logic")
    @classmethod
    def validate_tag_logic(cls, value):
        if value.upper() not in ["AND", "OR"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="tag_logic должен быть 'AND' или 'OR'"
            )
        return value.upper()

    @field_validator("min_price", "max_price", "min_piece_count", "max_piece_count")
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

    @field_validator("max_piece_count")
    @classmethod
    def validate_piece_count_range(cls, value, values):
        min_piece_count = values.data.get("min_piece_count")
        if value is not None and min_piece_count is not None and value < min_piece_count:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="max_piece_count не может быть меньше min_piece_count"
            )
        return value


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