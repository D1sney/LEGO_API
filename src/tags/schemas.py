# src/tags/schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class TagType(str, Enum):
    set = "set"
    minifigure = "minifigure"
    both = "both"

class TagBase(BaseModel):
    name: str = Field(..., description="Название тега", example="Хогвартс")
    tag_type: TagType = Field(..., description="Тип тега: set - только для наборов, minifigure - только для минифигурок, both - для обоих", example=TagType.both)

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Название тега", example="Хогвартс")
    tag_type: Optional[TagType] = Field(None, description="Тип тега: set - только для наборов, minifigure - только для минифигурок, both - для обоих", example=TagType.both)

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

class SetTagResponse(SetTagBase):
    class Config:
        from_attributes = True

class SetTagDelete(SetTagBase):
    pass

# Схемы для Minifigure_Tags
class MinifigureTagBase(BaseModel):
    minifigure_id: str = Field(..., description="ID минифигурки LEGO", example="hp150")
    tag_id: int = Field(..., description="ID тега", example=1)

class MinifigureTagCreate(MinifigureTagBase):
    pass

class MinifigureTagResponse(MinifigureTagBase):
    class Config:
        from_attributes = True

class MinifigureTagDelete(MinifigureTagBase):
    pass
