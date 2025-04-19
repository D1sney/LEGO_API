# src/tags/schemas.py
from pydantic import BaseModel
from typing import Optional, Literal

class TagBase(BaseModel):
    name: str
    tag_type: Literal["set", "minifigure", "both"]

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = None
    tag_type: Optional[Literal["set", "minifigure", "both"]] = None

class TagResponse(TagBase):
    tag_id: int

    class Config:
        from_attributes = True

class TagDelete(BaseModel):
    tag_id: int

# Схемы для Set_Tags
class SetTagBase(BaseModel):
    set_id: int
    tag_id: int

class SetTagCreate(SetTagBase):
    pass

class SetTagUpdate(BaseModel):
    set_id: Optional[int] = None
    tag_id: Optional[int] = None

class SetTagResponse(SetTagBase):
    class Config:
        from_attributes = True

class SetTagDelete(BaseModel):
    set_id: int
    tag_id: int

# Схемы для Minifigure_Tags
class MinifigureTagBase(BaseModel):
    minifigure_id: str
    tag_id: int

class MinifigureTagCreate(MinifigureTagBase):
    pass

class MinifigureTagUpdate(BaseModel):
    minifigure_id: Optional[str] = None
    tag_id: Optional[int] = None

class MinifigureTagResponse(MinifigureTagBase):
    class Config:
        from_attributes = True

class MinifigureTagDelete(BaseModel):
    minifigure_id: str
    tag_id: int