# src/tournaments/routes.py
from fastapi import APIRouter, Depends, Path, Query, status, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from src.database import get_db
from src.tournaments.schemas import (
    TournamentCreate,
    TournamentResponse,
    TournamentListResponse,
    TournamentVoteCreate,
    TournamentActionResponse,
    TournamentPairResponse
)
from src.tournaments.services import (
    create_tournament,
    vote_in_tournament,
    advance_tournament_stage
)
from src.tournaments.db import (
    get_db_tournament,
    get_db_tournament_with_pairs,
    get_db_tournaments,
    get_db_tournament_pair_with_details
)
from src.users.utils import get_current_user, get_admin_user
from src.users.models import User

router = APIRouter(
    prefix="/tournaments",
    tags=["tournaments"],
    responses={404: {"description": "Не найдено"}},
)

@router.post("/", response_model=TournamentResponse, status_code=status.HTTP_201_CREATED)
def create_new_tournament(
    tournament_data: TournamentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Создание нового турнира.
    
    - **title**: Название турнира
    - **type**: Тип турнира ('sets' или 'minifigures')
    - **search**: Поиск по имени (опционально)
    - **tag_names**: Фильтр по тегам через запятую (опционально)
    - **tag_logic**: Логика для тегов ('AND' или 'OR', опционально)
    - **min_price**: Минимальная цена (опционально)
    - **max_price**: Максимальная цена (опционально)
    - **min_piece_count**: Минимальное количество деталей для наборов (опционально)
    - **max_piece_count**: Максимальное количество деталей для наборов (опционально)
    - **stage_duration_hours**: Длительность каждой стадии турнира в часах (по умолчанию 24)
    """
    return create_tournament(db, tournament_data)

@router.get("/", response_model=List[TournamentListResponse])
def get_tournaments(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Получение списка турниров с пагинацией и фильтрацией по типу.
    
    - **skip**: Сколько турниров пропустить (для пагинации)
    - **limit**: Максимальное количество турниров (для пагинации)
    - **type**: Фильтр по типу турнира ('sets' или 'minifigures')
    """
    tournaments = get_db_tournaments(db, skip, limit, type)
    
    # Подсчитываем количество участников для каждого турнира
    result = []
    for tournament in tournaments:
        participants_count = len(tournament.participants)
        tournament_dict = {
            "tournament_id": tournament.tournament_id,
            "title": tournament.title,
            "type": tournament.type,
            "current_stage": tournament.current_stage,
            "stage_deadline": tournament.stage_deadline,
            "created_at": tournament.created_at,
            "participants_count": participants_count
        }
        result.append(tournament_dict)
    
    return result

@router.get("/{tournament_id}", response_model=TournamentResponse)
def get_tournament(
    tournament_id: int = Path(..., description="ID турнира"),
    db: Session = Depends(get_db)
):
    """
    Получение информации о турнире по ID.
    
    - **tournament_id**: ID турнира
    """
    tournament = get_db_tournament_with_pairs(db, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Турнир с ID {tournament_id} не найден"
        )
    
    return tournament

@router.post("/{tournament_id}/vote", response_model=TournamentActionResponse)
def vote_for_participant(
    tournament_id: int = Path(..., description="ID турнира"),
    vote_data: TournamentVoteCreate = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Голосование за участника в паре.
    
    - **tournament_id**: ID турнира
    - **pair_id**: ID пары
    - **voted_for**: ID участника, за которого голосует пользователь
    """
    return vote_in_tournament(db, tournament_id, vote_data, current_user.user_id)

@router.post("/{tournament_id}/advance", response_model=TournamentActionResponse)
def advance_to_next_stage(
    tournament_id: int = Path(..., description="ID турнира"),
    duration_hours: Optional[int] = Query(None, description="Длительность следующей стадии в часах"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Продвижение турнира на следующую стадию.
    Требуются права администратора.
    
    - **tournament_id**: ID турнира
    - **duration_hours**: Длительность следующей стадии в часах (если не указано, используется 24 часа)
    """
    return advance_tournament_stage(db, tournament_id, duration_hours)

@router.delete("/{tournament_id}", response_model=TournamentActionResponse)
def delete_tournament(
    tournament_id: int = Path(..., description="ID турнира"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Удаление турнира.
    Требуются права администратора.
    
    - **tournament_id**: ID турнира
    """
    tournament = get_db_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Турнир с ID {tournament_id} не найден"
        )
    
    db.delete(tournament)
    db.commit()
    
    return {"message": f"Турнир с ID {tournament_id} успешно удален"}

@router.get("/pairs/{pair_id}", response_model=TournamentPairResponse)
def get_tournament_pair(
    pair_id: int = Path(..., description="ID пары турнира"),
    db: Session = Depends(get_db)
):
    """
    Получение информации о паре турнира по ID.
    
    - **pair_id**: ID пары турнира
    """
    pair = get_db_tournament_pair_with_details(db, pair_id)
    if not pair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пара с ID {pair_id} не найдена"
        )
    
    return pair
