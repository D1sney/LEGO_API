# src/winners/routes.py
from fastapi import APIRouter, Depends, Path, Query, status, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from src.database import get_db
from src.winners.schemas import (
    TournamentWinnerCreate,
    TournamentWinnerUpdate,
    TournamentWinnerResponse,
    TournamentWinnerListResponse,
    TournamentWinnerActionResponse
)
from src.winners.services import (
    get_tournament_winners,
    get_tournament_winner,
    create_tournament_winner,
    create_tournament_winner_from_participant,
    update_tournament_winner,
    delete_tournament_winner
)
from src.users.utils import get_current_user, get_admin_user
from src.users.models import User
from src.logger import app_logger

router = APIRouter(
    prefix="/tournament-winners",
    tags=["tournament-winners"],
    responses={404: {"description": "Не найдено"}},
)

@router.get("/", response_model=TournamentWinnerListResponse)
def list_tournament_winners(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Получение списка победителей турниров.
    
    - **skip**: Сколько записей пропустить (для пагинации)
    - **limit**: Максимальное количество записей (для пагинации)
    - **type**: Фильтр по типу турнира ('sets' или 'minifigures')
    """
    result = get_tournament_winners(db, skip, limit, type)
    app_logger.info(f"Получено {len(result['winners'])} победителей турниров (skip={skip}, limit={limit}, type={type})")
    return result

@router.get("/tournament/{tournament_id}", response_model=TournamentWinnerResponse)
def get_winner_of_tournament(
    tournament_id: int = Path(..., description="ID турнира"),
    db: Session = Depends(get_db)
):
    """
    Получение победителя турнира по ID турнира.
    
    - **tournament_id**: ID турнира
    """
    winner = get_tournament_winner(db, tournament_id)
    app_logger.info(f"Получен победитель турнира ID: {tournament_id}")
    return winner

@router.post("/tournament/{tournament_id}", response_model=TournamentWinnerResponse, status_code=status.HTTP_201_CREATED)
def add_tournament_winner(
    winner_data: TournamentWinnerCreate,
    tournament_id: int = Path(..., description="ID турнира"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Создание записи о победителе турнира (для ручного назначения).
    Требуются права администратора.
    
    - **tournament_id**: ID турнира
    - **set_id**: ID набора-победителя (опционально)
    - **minifigure_id**: ID минифигурки-победителя (опционально)
    - **total_votes**: Общее количество голосов (опционально)
    
    Необходимо указать либо set_id, либо minifigure_id в зависимости от типа турнира.
    """
    winner = create_tournament_winner(db, tournament_id, winner_data)
    app_logger.info(f"Добавлен победитель турнира {tournament_id}")
    return winner

@router.post("/tournament/{tournament_id}/from-participant/{participant_id}", response_model=TournamentWinnerResponse, status_code=status.HTTP_201_CREATED)
def add_winner_from_participant(
    tournament_id: int = Path(..., description="ID турнира"),
    participant_id: int = Path(..., description="ID участника-победителя"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Создание записи о победителе турнира на основе участника.
    Требуются права администратора.
    
    - **tournament_id**: ID турнира
    - **participant_id**: ID участника-победителя
    """
    winner = create_tournament_winner_from_participant(db, tournament_id, participant_id)
    app_logger.info(f"Добавлен победитель турнира {tournament_id} из участника {participant_id}")
    return winner

@router.put("/{winner_id}", response_model=TournamentWinnerResponse)
def update_winner(
    winner_data: TournamentWinnerUpdate,
    winner_id: int = Path(..., description="ID записи о победителе"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Обновление информации о победителе турнира.
    Требуются права администратора.
    
    - **winner_id**: ID записи о победителе
    - **set_id**: ID нового набора-победителя (опционально)
    - **minifigure_id**: ID новой минифигурки-победителя (опционально)
    - **total_votes**: Новое общее количество голосов (опционально)
    """
    winner = update_tournament_winner(db, winner_id, winner_data)
    app_logger.info(f"Обновлен победитель турнира ID: {winner_id}")
    return winner

@router.delete("/{winner_id}", response_model=TournamentWinnerActionResponse)
def remove_tournament_winner(
    winner_id: int = Path(..., description="ID записи о победителе"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Удаление записи о победителе турнира.
    Требуются права администратора.
    
    - **winner_id**: ID записи о победителе
    """
    result = delete_tournament_winner(db, winner_id)
    app_logger.info(f"Удален победитель турнира ID: {winner_id}")
    return result 