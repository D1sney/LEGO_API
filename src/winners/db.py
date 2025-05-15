from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from datetime import datetime
from typing import List, Optional, Tuple

from src.winners.models import TournamentWinner
from src.tournaments.models import Tournament
from src.tournaments.models import TournamentParticipant

def get_db_tournament_winner(db: Session, tournament_id: int) -> Optional[TournamentWinner]:
    """Получение победителя турнира по ID турнира"""
    return (
        db.query(TournamentWinner)
        .options(
            joinedload(TournamentWinner.set),
            joinedload(TournamentWinner.minifigure)
        )
        .filter(TournamentWinner.tournament_id == tournament_id)
        .first()
    )

def get_db_tournament_winner_by_id(db: Session, winner_id: int) -> Optional[TournamentWinner]:
    """Получение победителя турнира по ID записи победителя"""
    return (
        db.query(TournamentWinner)
        .options(
            joinedload(TournamentWinner.set),
            joinedload(TournamentWinner.minifigure)
        )
        .filter(TournamentWinner.winner_id == winner_id)
        .first()
    )

def get_db_tournament_winners(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    type: Optional[str] = None
) -> Tuple[List[TournamentWinner], int]:
    """Получение списка победителей турниров с пагинацией и фильтрацией"""
    query = db.query(TournamentWinner)
    
    if type:
        query = query.join(Tournament).filter(Tournament.type == type)
    
    # Считаем общее количество
    total = query.count()
    
    # Применяем пагинацию
    winners = query.options(
        joinedload(TournamentWinner.set),
        joinedload(TournamentWinner.minifigure),
        joinedload(TournamentWinner.tournament)
    ).offset(skip).limit(limit).all()
    
    return winners, total

def create_db_tournament_winner(
    db: Session, 
    tournament_id: int, 
    set_id: Optional[int] = None,
    minifigure_id: Optional[str] = None,
    total_votes: int = 0
) -> TournamentWinner:
    """Создание записи о победителе турнира"""
    winner = TournamentWinner(
        tournament_id=tournament_id,
        set_id=set_id,
        minifigure_id=minifigure_id,
        total_votes=total_votes
    )
    db.add(winner)
    db.commit()
    db.refresh(winner)
    return winner

def update_db_tournament_winner(
    db: Session, 
    winner_id: int, 
    set_id: Optional[int] = None,
    minifigure_id: Optional[str] = None,
    total_votes: Optional[int] = None
) -> Optional[TournamentWinner]:
    """Обновление информации о победителе турнира"""
    winner = db.query(TournamentWinner).filter(TournamentWinner.winner_id == winner_id).first()
    if not winner:
        return None
    
    # Обновляем только те поля, которые указаны
    if set_id is not None:
        winner.set_id = set_id
        winner.minifigure_id = None  # Сбрасываем minifigure_id, так как может быть только один из них
    
    if minifigure_id is not None:
        winner.minifigure_id = minifigure_id
        winner.set_id = None  # Сбрасываем set_id, так как может быть только один из них
    
    if total_votes is not None:
        winner.total_votes = total_votes
    
    db.commit()
    db.refresh(winner)
    return winner

def delete_db_tournament_winner(db: Session, winner_id: int) -> bool:
    """Удаление записи о победителе турнира"""
    winner = db.query(TournamentWinner).filter(TournamentWinner.winner_id == winner_id).first()
    if not winner:
        return False
    
    db.delete(winner)
    db.commit()
    return True

def get_participant_details(db: Session, participant_id: int) -> Tuple[Optional[int], Optional[str]]:
    """Получает set_id и minifigure_id участника турнира"""
    participant = db.query(TournamentParticipant).filter(
        TournamentParticipant.participant_id == participant_id
    ).first()
    
    if not participant:
        return None, None
    
    return participant.set_id, participant.minifigure_id 