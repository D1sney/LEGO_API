# src/tags/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Literal

class TagBase(BaseModel):
    name: str = Field(..., description="Название тега", example="Хогвартс")
    tag_type: Literal["set", "minifigure", "both"] = Field(..., description="Тип тега: set - только для наборов, minifigure - только для минифигурок, both - для обоих", example="both")

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Название тега", example="Хогвартс")
    tag_type: Optional[Literal["set", "minifigure", "both"]] = Field(None, description="Тип тега: set - только для наборов, minifigure - только для минифигурок, both - для обоих", example="both")

class TagResponse(TagBase):
    tag_id: int = Field(..., description="Уникальный идентификатор тега")

    class Config:
        from_attributes = True

class TagDelete(BaseModel):
    tag_id: int = Field(..., description="Уникальный идентификатор тега для удаления")

# Схемы для Set_Tags
class SetTagBase(BaseModel):
    set_id: int = Field(..., description="ID набора LEGO", example=75968)
    tag_id: int = Field(..., description="ID тега", example=1)

class SetTagCreate(SetTagBase):
    pass

class SetTagUpdate(BaseModel):
    set_id: Optional[int] = Field(None, description="ID набора LEGO", example=75968)
    tag_id: Optional[int] = Field(None, description="ID тега", example=1)

class SetTagResponse(SetTagBase):
    class Config:
        from_attributes = True

class SetTagDelete(BaseModel):
    set_id: int = Field(..., description="ID набора LEGO", example=75968)
    tag_id: int = Field(..., description="ID тега", example=1)

# Схемы для Minifigure_Tags
class MinifigureTagBase(BaseModel):
    minifigure_id: str = Field(..., description="ID минифигурки LEGO", example="hp150")
    tag_id: int = Field(..., description="ID тега", example=1)

class MinifigureTagCreate(MinifigureTagBase):
    pass

class MinifigureTagUpdate(BaseModel):
    minifigure_id: Optional[str] = Field(None, description="ID минифигурки LEGO", example="hp150")
    tag_id: Optional[int] = Field(None, description="ID тега", example=1)

class MinifigureTagResponse(MinifigureTagBase):
    class Config:
        from_attributes = True

class MinifigureTagDelete(BaseModel):
    minifigure_id: str = Field(..., description="ID минифигурки LEGO", example="hp150")
    tag_id: int = Field(..., description="ID тега", example=1)