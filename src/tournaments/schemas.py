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
    theme: Optional[str] = Field(None, description="Фильтр по теме (для наборов)")
    sub_theme: Optional[str] = Field(None, description="Фильтр по подтеме (для наборов)")
    tag_name: Optional[str] = Field(None, description="Фильтр по тегу")
    min_price: Optional[float] = Field(None, description="Минимальная цена")
    max_price: Optional[float] = Field(None, description="Максимальная цена")
    min_year: Optional[int] = Field(None, description="Минимальный год выпуска (для наборов)")
    max_year: Optional[int] = Field(None, description="Максимальный год выпуска (для наборов)")

    @field_validator("type")
    def validate_type(cls, v):
        if v not in ["sets", "minifigures"]:
            raise ValueError("Тип турнира должен быть 'sets' или 'minifigures'")
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
    user_id: int
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
