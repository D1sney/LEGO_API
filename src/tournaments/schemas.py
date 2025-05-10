# src/tournaments/schemas.py
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional, Union, Dict, Any
from src.sets.schemas import SetResponse
from src.minifigures.schemas import MinifigureResponse
from src.users.schemas import UserResponse

# Входящие данные (запросы)

class TournamentCreate(BaseModel):
    title: str = Field(..., description="Название турнира")
    type: str = Field(..., description="Тип турнира: 'sets' или 'minifigures'")
    # Параметры для фильтрации
    search: Optional[str] = Field(None, description="Поиск по имени")
    tag_names: Optional[str] = Field(None, description="Фильтр по тегам (через запятую)")
    tag_logic: Optional[str] = Field("AND", description="Логика для тегов: 'AND' (все теги должны совпадать) или 'OR' (любой из тегов)")
    min_price: Optional[float] = Field(None, description="Минимальная цена")
    max_price: Optional[float] = Field(None, description="Максимальная цена")
    min_piece_count: Optional[int] = Field(None, description="Минимальное количество деталей (для наборов)")
    max_piece_count: Optional[int] = Field(None, description="Максимальное количество деталей (для наборов)")
    stage_duration_hours: Optional[int] = Field(24, description="Длительность каждой стадии турнира в часах")

    @field_validator("type")
    def validate_type(cls, v):
        if v not in ["sets", "minifigures"]:
            raise ValueError("Тип турнира должен быть 'sets' или 'minifigures'")
        return v

    @field_validator("tag_logic")
    def validate_tag_logic(cls, v):
        if v not in ["AND", "OR"]:
            raise ValueError("Логика для тегов должна быть 'AND' или 'OR'")
        return v

    @field_validator("stage_duration_hours")
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError("Длительность стадии должна быть положительным числом")
        return v

class TournamentVoteCreate(BaseModel):
    pair_id: int = Field(..., description="ID пары для голосования")
    voted_for: int = Field(..., description="ID участника, за которого голосуют")

# Исходящие данные (ответы)

class TournamentParticipantBase(BaseModel):
    participant_id: int
    position: int
    set_id: Optional[int] = None
    minifigure_id: Optional[str] = None

    class Config:
        orm_mode = True

class TournamentParticipantResponse(TournamentParticipantBase):
    set: Optional[SetResponse] = None
    minifigure: Optional[MinifigureResponse] = None

class TournamentVoteResponse(BaseModel):
    vote_id: int
    user_id: str
    voted_for: int
    created_at: datetime

    class Config:
        orm_mode = True

class TournamentPairBase(BaseModel):
    pair_id: int
    stage: str
    participant1_id: int
    participant2_id: Optional[int] = None
    winner_id: Optional[int] = None

    class Config:
        orm_mode = True

class TournamentPairResponse(TournamentPairBase):
    participant1: TournamentParticipantResponse
    participant2: Optional[TournamentParticipantResponse] = None
    winner: Optional[TournamentParticipantResponse] = None
    votes: List[TournamentVoteResponse] = []

class TournamentBase(BaseModel):
    tournament_id: int
    title: str
    type: str
    current_stage: str
    stage_deadline: datetime
    created_at: datetime

    class Config:
        orm_mode = True

class TournamentResponse(TournamentBase):
    participants: List[TournamentParticipantResponse] = []
    pairs: List[TournamentPairResponse] = []

# Упрощенные схемы для списка турниров
class TournamentListResponse(TournamentBase):
    participants_count: int

# Ответы API
class TournamentActionResponse(BaseModel):
    message: str
