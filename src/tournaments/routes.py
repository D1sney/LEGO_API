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
    TournamentActionResponse
)
from src.tournaments.services import (
    create_tournament,
    vote_in_tournament,
    advance_tournament_stage
)
from src.tournaments.db import (
    get_db_tournament,
    get_db_tournament_with_pairs,
    get_db_tournaments
)
from src.users.utils import get_current_user

router = APIRouter(
    prefix="/tournaments",
    tags=["tournaments"],
    responses={404: {"description": "Не найдено"}},
)

@router.post("/", response_model=TournamentResponse, status_code=status.HTTP_201_CREATED)
def create_new_tournament(
    tournament_data: TournamentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Создание нового турнира.
    
    - **title**: Название турнира
    - **type**: Тип турнира ('sets' или 'minifigures')
    - **search**: Поиск по имени (опционально)
    - **theme**: Фильтр по теме наборов (опционально)
    - **sub_theme**: Фильтр по подтеме наборов (опционально)
    - **tag_name**: Фильтр по тегу (опционально)
    - **min_price**: Минимальная цена (опционально)
    - **max_price**: Максимальная цена (опционально)
    - **min_year**: Минимальный год выпуска для наборов (опционально)
    - **max_year**: Максимальный год выпуска для наборов (опционально)
    """
    # Проверяем, что пользователь имеет права администратора
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания турнира"
        )
    
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
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Продвижение турнира на следующую стадию.
    Требуются права администратора.
    
    - **tournament_id**: ID турнира
    """
    # Проверяем, что пользователь имеет права администратора
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для продвижения турнира"
        )
    
    return advance_tournament_stage(db, tournament_id)

@router.delete("/{tournament_id}", response_model=TournamentActionResponse)
def delete_tournament(
    tournament_id: int = Path(..., description="ID турнира"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Удаление турнира.
    Требуются права администратора.
    
    - **tournament_id**: ID турнира
    """
    # Проверяем, что пользователь имеет права администратора
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления турнира"
        )
    
    tournament = get_db_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Турнир с ID {tournament_id} не найден"
        )
    
    db.delete(tournament)
    db.commit()
    
    return {"message": f"Турнир с ID {tournament_id} успешно удален"}
