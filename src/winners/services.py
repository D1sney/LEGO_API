from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.winners.models import TournamentWinner
from src.winners.schemas import TournamentWinnerCreate, TournamentWinnerUpdate
from src.tournaments.models import Tournament, TournamentParticipant, TournamentVote
from src.winners.db import (
    get_db_tournament_winner,
    get_db_tournament_winner_by_id,
    get_db_tournament_winners,
    create_db_tournament_winner,
    update_db_tournament_winner,
    delete_db_tournament_winner,
    get_participant_details,
    count_participant_votes,
    check_tournament_type
)
from src.tournaments.db import get_db_tournament

def get_tournament_winners(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Получение списка победителей турниров
    """
    winners, total = get_db_tournament_winners(db, skip, limit, type)
    return {
        "winners": winners,
        "total": total
    }

def get_tournament_winner(db: Session, tournament_id: int) -> TournamentWinner:
    """
    Получение победителя турнира
    """
    winner = get_db_tournament_winner(db, tournament_id)
    if not winner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Победитель турнира не найден"
        )
    return winner

def create_tournament_winner_from_participant(
    db: Session,
    tournament_id: int,
    participant_id: int
) -> TournamentWinner:
    """
    Создание записи о победителе турнира на основе участника
    """
    # Проверяем существование турнира
    tournament = get_db_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Турнир не найден"
        )
    
    # Проверяем, что турнир завершен
    if tournament.current_stage != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя назначить победителя для незавершенного турнира"
        )
    
    # Проверяем, что победитель еще не назначен
    existing_winner = get_db_tournament_winner(db, tournament_id)
    if existing_winner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Победитель для этого турнира уже назначен"
        )
    
    # Получаем информацию об участнике
    set_id, minifigure_id = get_participant_details(db, participant_id)
    if set_id is None and minifigure_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Указанный участник не найден"
        )
    
    # Подсчитываем общее количество голосов за победителя за все стадии
    total_votes = count_participant_votes(db, participant_id)
    
    # Создаем запись о победителе турнира
    winner = create_db_tournament_winner(
        db, 
        tournament_id=tournament_id,
        set_id=set_id,
        minifigure_id=minifigure_id,
        total_votes=total_votes
    )
    return winner

def create_tournament_winner(
    db: Session, 
    tournament_id: int, 
    winner_data: TournamentWinnerCreate
) -> TournamentWinner:
    """
    Ручное создание записи о победителе турнира
    """
    # Проверяем существование турнира
    tournament = get_db_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Турнир не найден"
        )
    
    # Проверяем, что турнир завершен
    if tournament.current_stage != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя назначить победителя для незавершенного турнира"
        )
    
    # Проверяем, что победитель еще не назначен
    existing_winner = get_db_tournament_winner(db, tournament_id)
    if existing_winner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Победитель для этого турнира уже назначен"
        )
    
    # Проверяем, что указан хотя бы один из идентификаторов: set_id или minifigure_id
    if winner_data.set_id is None and winner_data.minifigure_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать ID набора или ID минифигурки"
        )
    
    # Если указан set_id, проверяем его существование
    if winner_data.set_id is not None:
        set_tournament_check = check_tournament_type(db, tournament_id, "sets")
        
        if not set_tournament_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Указанный турнир не является турниром наборов"
            )
    
    # Если указан minifigure_id, проверяем его существование
    if winner_data.minifigure_id is not None:
        minifigure_tournament_check = check_tournament_type(db, tournament_id, "minifigures")
        
        if not minifigure_tournament_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Указанный турнир не является турниром минифигурок"
            )
    
    # Создаем запись о победителе
    winner = create_db_tournament_winner(
        db,
        tournament_id=tournament_id,
        set_id=winner_data.set_id,
        minifigure_id=winner_data.minifigure_id,
        total_votes=winner_data.total_votes
    )
    return winner

def update_tournament_winner(
    db: Session, 
    winner_id: int, 
    winner_data: TournamentWinnerUpdate
) -> TournamentWinner:
    """
    Обновление информации о победителе турнира
    """
    # Проверяем существование победителя
    winner = get_db_tournament_winner_by_id(db, winner_id)
    if not winner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Победитель не найден"
        )
    
    # Получаем информацию о турнире
    tournament = get_db_tournament(db, winner.tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Турнир не найден"
        )
    
    # Проверяем, что данные соответствуют типу турнира
    if winner_data.set_id is not None and tournament.type != "sets":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя назначить набор победителем в турнире минифигурок"
        )
    
    if winner_data.minifigure_id is not None and tournament.type != "minifigures":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя назначить минифигурку победителем в турнире наборов"
        )
    
    # Обновляем информацию о победителе
    updated_winner = update_db_tournament_winner(
        db,
        winner_id=winner_id,
        set_id=winner_data.set_id,
        minifigure_id=winner_data.minifigure_id,
        total_votes=winner_data.total_votes
    )
    return updated_winner

def delete_tournament_winner(db: Session, winner_id: int) -> Dict[str, str]:
    """
    Удаление записи о победителе турнира
    """
    # Проверяем существование победителя
    winner = get_db_tournament_winner_by_id(db, winner_id)
    if not winner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Победитель не найден"
        )
    
    # Удаляем запись
    result = delete_db_tournament_winner(db, winner_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Победитель не найден"
        )
    
    return {"message": f"Победитель турнира с ID {winner_id} удален"} 