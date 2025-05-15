# src/winners/schemas.py
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional, Dict, Any
from src.sets.schemas import SetResponse
from src.minifigures.schemas import MinifigureResponse

# Входящие данные (запросы)
class TournamentWinnerCreate(BaseModel):
    set_id: Optional[int] = Field(None, description="ID набора-победителя")
    minifigure_id: Optional[str] = Field(None, description="ID минифигурки-победителя")
    total_votes: Optional[int] = Field(0, description="Общее количество голосов, полученных победителем")
    
    @field_validator("set_id", "minifigure_id")
    def validate_winner_type(cls, v, info):
        field_name = info.field_name
        values = info.data
        
        if field_name == "set_id" and v is not None and values.get("minifigure_id") is not None:
            raise ValueError("Можно указать только один из параметров: set_id или minifigure_id")
        if field_name == "minifigure_id" and v is not None and values.get("set_id") is not None:
            raise ValueError("Можно указать только один из параметров: set_id или minifigure_id")
        
        return v
    
    @field_validator("total_votes")
    def validate_total_votes(cls, v):
        if v < 0:
            raise ValueError("Количество голосов не может быть отрицательным")
        return v

class TournamentWinnerUpdate(BaseModel):
    set_id: Optional[int] = Field(None, description="ID набора-победителя")
    minifigure_id: Optional[str] = Field(None, description="ID минифигурки-победителя")
    total_votes: Optional[int] = Field(None, description="Общее количество голосов")
    
    @field_validator("set_id", "minifigure_id")
    def validate_winner_type(cls, v, info):
        field_name = info.field_name
        values = info.data
        
        if field_name == "set_id" and v is not None and values.get("minifigure_id") is not None:
            raise ValueError("Можно указать только один из параметров: set_id или minifigure_id")
        if field_name == "minifigure_id" and v is not None and values.get("set_id") is not None:
            raise ValueError("Можно указать только один из параметров: set_id или minifigure_id")
        
        return v
    
    @field_validator("total_votes")
    def validate_total_votes(cls, v):
        if v is not None and v < 0:
            raise ValueError("Количество голосов не может быть отрицательным")
        return v

# Исходящие данные (ответы)
class TournamentWinnerBase(BaseModel):
    winner_id: int
    tournament_id: int
    set_id: Optional[int] = None
    minifigure_id: Optional[str] = None
    total_votes: int
    won_at: datetime
    
    class Config:
        orm_mode = True

class TournamentWinnerResponse(TournamentWinnerBase):
    set: Optional[SetResponse] = None
    minifigure: Optional[MinifigureResponse] = None

class TournamentWinnerListResponse(BaseModel):
    winners: List[TournamentWinnerResponse]
    total: int

# Ответы API
class TournamentWinnerActionResponse(BaseModel):
    message: str 