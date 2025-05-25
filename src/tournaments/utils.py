# src/tournaments/utils.py
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.tournaments.models import Tournament, TournamentParticipant, TournamentPair, TournamentVote
from src.sets.db import get_db_sets
from src.minifigures.db import get_db_minifigures
from src.tournaments.schemas import TournamentCreate
from src.logger import app_logger

def get_tournament_participants(
    db: Session, 
    tournament_data: TournamentCreate
) -> List[Any]:
    """
    Получение участников турнира в соответствии с фильтрами
    """
    # Фильтры для наборов
    if tournament_data.type == "sets":
        filters = {
            "limit": 1000,  # Большой лимит для получения всех подходящих наборов
            "search": tournament_data.search,
            "tag_names": tournament_data.tag_names,
            "tag_logic": tournament_data.tag_logic,
            "min_price": tournament_data.min_price,
            "max_price": tournament_data.max_price,
            "min_piece_count": tournament_data.min_piece_count if hasattr(tournament_data, "min_piece_count") else None,
            "max_piece_count": tournament_data.max_piece_count if hasattr(tournament_data, "max_piece_count") else None,
        }
        # Удаляем None значения
        filters = {k: v for k, v in filters.items() if v is not None}
        participants = list(get_db_sets(db, **filters))
    
    # Фильтры для минифигурок
    else:
        filters = {
            "limit": 1000,
            "search": tournament_data.search,
            "tag_names": tournament_data.tag_names,
            "tag_logic": tournament_data.tag_logic,
            "min_price": tournament_data.min_price,
            "max_price": tournament_data.max_price
        }
        # Удаляем None значения
        filters = {k: v for k, v in filters.items() if v is not None}
        participants = list(get_db_minifigures(db, **filters))
    
    return participants

def round_to_power_of_two(n: int) -> int:
    """
    Округление до ближайшей степени двойки
    Например: 25 -> 32, 15 -> 16, 40 -> 64
    """
    if n <= 1:
        return 2  # Минимум 2 участника
    
    return 2 ** math.ceil(math.log2(n))

def determine_first_stage(num_participants: int) -> str:
    """
    Определение начальной стадии турнира в зависимости от числа участников
    """
    if num_participants <= 2:
        return "final"
    elif num_participants <= 4:
        return "semifinal"
    elif num_participants <= 8:
        return "quarterfinal"
    elif num_participants <= 16:
        return "1/8"
    elif num_participants <= 32:
        return "1/16"
    elif num_participants <= 64:
        return "1/32"
    else:
        return "1/64"

def generate_tournament_pairs(
    db: Session,
    tournament: Tournament,
    participants: List[TournamentParticipant],
    first_stage: str,
    target_num: int
) -> List[TournamentPair]:
    """
    Генерация пар для первой стадии турнира
    """
    # Создаём список пар
    pairs = []
    num_pairs = target_num // 2
    participant_index = 0

    # Шаг 1: Заполняем participant1 для каждой пары
    for _ in range(num_pairs):
        participant1_id = participants[participant_index].participant_id if participant_index < len(participants) else None
        pairs.append(TournamentPair(
            tournament_id=tournament.tournament_id,
            stage=first_stage,
            participant1_id=participant1_id
        ))
        participant_index += 1

    # Шаг 2: Заполняем participant2 для каждой пары, если участники остались
    for i, pair in enumerate(pairs):
        if participant_index < len(participants):
            pair.participant2_id = participants[participant_index].participant_id
            participant_index += 1

    db.add_all(pairs)
    db.flush()
    app_logger.info(f"Сгенерировано {len(pairs)} пар для стадии {first_stage} турнира {tournament.tournament_id}")
    return pairs

def get_next_stage(current_stage: str) -> Optional[str]:
    """
    Получение следующей стадии турнира
    """
    stages = ["1/64", "1/32", "1/16", "1/8", "quarterfinal", "semifinal", "final", "completed"]
    try:
        current_index = stages.index(current_stage)
        if current_index + 1 < len(stages):
            return stages[current_index + 1]
        return None
    except ValueError:
        return None

def calculate_winners(db: Session, pairs: List[TournamentPair]) -> List[int]:
    """
    Подсчет голосов и определение победителей для каждой пары
    """
    winners = []
    
    for pair in pairs:
        # Если второго участника нет, первый автоматически побеждает
        if not pair.participant2_id:
            pair.winner_id = pair.participant1_id
            winners.append(pair.participant1_id)
            continue
        
        # Подсчет голосов
        votes = db.query(
            TournamentVote.voted_for,
            func.count(TournamentVote.voted_for).label("vote_count")
        ).filter(
            TournamentVote.pair_id == pair.pair_id
        ).group_by(TournamentVote.voted_for).all()
        
        votes_dict = {voted_for: count for voted_for, count in votes}
        votes_p1 = votes_dict.get(pair.participant1_id, 0)
        votes_p2 = votes_dict.get(pair.participant2_id, 0)
        
        # Определение победителя
        if votes_p1 > votes_p2:
            pair.winner_id = pair.participant1_id
            winners.append(pair.participant1_id)
        elif votes_p2 > votes_p1:
            pair.winner_id = pair.participant2_id
            winners.append(pair.participant2_id)
        else:
            # Если голоса равны, выбираем случайно
            pair.winner_id = random.choice([pair.participant1_id, pair.participant2_id])
            winners.append(pair.winner_id)
    
    app_logger.info(f"Победители определены для {len(pairs)} пар")
    return winners

def generate_next_stage_pairs(
    db: Session,
    tournament: Tournament,
    winner_ids: List[int]
) -> List[TournamentPair]:
    """
    Генерация пар для следующей стадии турнира
    """
    pairs = []
    
    for i in range(0, len(winner_ids), 2):
        participant1_id = winner_ids[i]
        # Если число победителей нечетное, последняя пара будет иметь только одного участника
        participant2_id = winner_ids[i + 1] if i + 1 < len(winner_ids) else None
        
        pair = TournamentPair(
            tournament_id=tournament.tournament_id,
            stage=tournament.current_stage,
            participant1_id=participant1_id,
            participant2_id=participant2_id
        )
        pairs.append(pair)
    
    db.add_all(pairs)
    db.flush()
    app_logger.info(f"Сгенерировано {len(pairs)} пар для стадии {tournament.current_stage} турнира {tournament.tournament_id}")
    return pairs
