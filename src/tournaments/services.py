# src/tournaments/services.py
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple, Union
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.tournaments.models import Tournament, TournamentParticipant, TournamentPair, TournamentVote
from src.tournaments.schemas import TournamentCreate, TournamentVoteCreate
from src.tournaments.db import (
    get_db_tournament,
    get_db_tournament_pair,
    get_db_tournament_vote,
    get_db_current_stage_pairs,
    create_db_tournament_vote
)
from src.tournaments.utils import (
    get_tournament_participants,
    round_to_power_of_two,
    determine_first_stage,
    generate_tournament_pairs,
    get_next_stage,
    calculate_winners,
    generate_next_stage_pairs
)

def create_tournament(db: Session, tournament_data: TournamentCreate) -> Tournament:
    """
    Создание нового турнира
    """
    # Получаем участников в соответствии с фильтрами
    participants = get_tournament_participants(db, tournament_data)
    
    if not participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не найдено участников, соответствующих заданным критериям"
        )
    
    # Перемешиваем участников
    random.shuffle(participants)
    
    # Определяем количество участников и стадию
    num_participants = len(participants)
    target_num = round_to_power_of_two(num_participants)
    first_stage = determine_first_stage(target_num)
    
    # Создаем турнир
    tournament = Tournament(
        title=tournament_data.title,
        type=tournament_data.type,
        current_stage=first_stage,
        stage_deadline=datetime.now(timezone.utc) + timedelta(hours=tournament_data.stage_duration_hours)  # Используем указанное количество часов
    )
    db.add(tournament)
    db.flush()
    
    # Создаем участников турнира
    tournament_participants = []
    for i, participant in enumerate(participants):
        tournament_participant = TournamentParticipant(
            tournament_id=tournament.tournament_id,
            set_id=participant.set_id if tournament_data.type == "sets" else None,
            minifigure_id=participant.minifigure_id if tournament_data.type == "minifigures" else None,
            position=i + 1
        )
        tournament_participants.append(tournament_participant)
    
    db.add_all(tournament_participants)
    db.flush()
    
    # Генерируем пары для первой стадии
    generate_tournament_pairs(db, tournament, tournament_participants, first_stage, target_num)
    
    db.commit()
    return tournament

def vote_in_tournament(
    db: Session, 
    tournament_id: int, 
    vote_data: TournamentVoteCreate, 
    user_id: int
) -> Dict[str, str]:
    """
    Голосование в турнире
    """
    # Проверяем существование турнира
    tournament = get_db_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Турнир не найден"
        )
    
    # Проверяем, что турнир не завершен
    if tournament.current_stage == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Турнир завершен"
        )
    
    # Проверяем, что время голосования не истекло
    if datetime.now(timezone.utc) > tournament.stage_deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время голосования для текущей стадии истекло"
        )
    
    # Проверяем существование пары
    pair = get_db_tournament_pair(db, vote_data.pair_id)
    if not pair or pair.tournament_id != tournament_id or pair.stage != tournament.current_stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пара не найдена или не принадлежит текущей стадии турнира"
        )
    
    # Проверяем, что voted_for - это ID одного из участников пары
    if vote_data.voted_for not in [pair.participant1_id, pair.participant2_id]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Голосовать можно только за одного из участников пары"
        )
    
    # Проверяем, не голосовал ли пользователь уже за эту пару
    existing_vote = get_db_tournament_vote(db, vote_data.pair_id, user_id)
    if existing_vote:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже проголосовали за эту пару"
        )
    
    # Создаем голос
    create_db_tournament_vote(db, vote_data.pair_id, user_id, vote_data.voted_for)
    
    return {"message": "Голос успешно учтен"}

def advance_tournament_stage(db: Session, tournament_id: int, duration_hours: Optional[int] = None) -> Dict[str, str]:
    """
    Продвижение турнира на следующую стадию
    
    Args:
        db: Сессия базы данных
        tournament_id: ID турнира
        duration_hours: Длительность следующей стадии в часах (если не указано, используется 24 часа)
    """
    # Проверяем существование турнира
    tournament = get_db_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Турнир не найден"
        )
    
    # Проверяем, что турнир не завершен
    if tournament.current_stage == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Турнир уже завершен"
        )
    
    # Проверяем, что время текущей стадии истекло
    if datetime.now(timezone.utc) < tournament.stage_deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Текущая стадия еще не завершена. Осталось: {tournament.stage_deadline - datetime.now(timezone.utc)}"
        )
    
    # Получаем пары текущей стадии
    pairs = get_db_current_stage_pairs(db, tournament_id)
    if not pairs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нет пар для текущей стадии"
        )
    
    # Считаем победителей
    winner_ids = calculate_winners(db, pairs)
    
    # Определяем следующую стадию
    next_stage = get_next_stage(tournament.current_stage)
    if not next_stage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно определить следующую стадию"
        )
    
    # Обновляем стадию турнира
    tournament.current_stage = next_stage
    
    # Если это финал и он уже сыгран, отмечаем турнир как завершенный
    if next_stage == "completed":
        tournament.stage_deadline = datetime.now(timezone.utc)
        db.commit()
        return {"message": "Турнир успешно завершен"}
    
    # Устанавливаем новый дедлайн для следующей стадии
    # Если duration_hours ровно или меньше 0, используем 24 часа (1 день)
    hours = duration_hours if duration_hours is not None and duration_hours > 0 else 24
    tournament.stage_deadline = datetime.now(timezone.utc) + timedelta(hours=hours)
    
    # Создаем пары для следующей стадии
    generate_next_stage_pairs(db, tournament, winner_ids)
    
    db.commit()
    return {"message": f"Турнир успешно продвинут на стадию {next_stage}"} 