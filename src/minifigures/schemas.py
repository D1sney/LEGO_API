# src/minifigures/schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class MinifigureBase(BaseModel):
    minifigure_id: str = Field(..., description="Уникальный идентификатор минифигурки (например, hp150)", example="hp150")
    character_name: str = Field(..., description="Имя персонажа", example="Гарри Поттер")
    name: str = Field(..., description="Название минифигурки", example="Harry Potter, Gryffindor Robe")
    face_photo_id: Optional[int] = Field(None, description="ID главного фото минифигурки")

class MinifigureCreate(MinifigureBase):
    pass

class MinifigureUpdate(BaseModel):
    character_name: Optional[str] = Field(None, description="Имя персонажа", example="Гарри Поттер")
    name: Optional[str] = Field(None, description="Название минифигурки", example="Harry Potter, Gryffindor Robe")
    face_photo_id: Optional[int] = Field(None, description="ID главного фото минифигурки")

class MinifigureResponse(MinifigureBase):
    class Config:
        from_attributes = True

class MinifigureDelete(BaseModel):
    minifigure_id: str = Field(..., description="Уникальный идентификатор минифигурки для удаления", example="hp150")