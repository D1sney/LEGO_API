# src/tournaments/db.py
from sqlalchemy.orm import Session, joinedload, contains_eager
from sqlalchemy import and_, or_, func
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status

from src.tournaments.models import Tournament, TournamentParticipant, TournamentPair, TournamentVote
from src.tournaments.schemas import TournamentCreate

def get_db_tournament(db: Session, tournament_id: int) -> Optional[Tournament]:
    """Получение турнира по ID с загрузкой всех связанных данных"""
    return db.query(Tournament).filter(Tournament.tournament_id == tournament_id).first()

def get_db_tournament_with_participants(db: Session, tournament_id: int) -> Optional[Tournament]:
    """Получение турнира по ID с участниками"""
    return (
        db.query(Tournament)
        .options(joinedload(Tournament.participants))
        .filter(Tournament.tournament_id == tournament_id)
        .first()
    )

def get_db_tournament_with_pairs(db: Session, tournament_id: int) -> Optional[Tournament]:
    """Получение турнира по ID с парами"""
    tournament = (
        db.query(Tournament)
        .options(
            joinedload(Tournament.pairs)
            .joinedload(TournamentPair.participant1)
        )
        .options(
            joinedload(Tournament.pairs)
            .joinedload(TournamentPair.participant2)
        )
        .options(
            joinedload(Tournament.pairs)
            .joinedload(TournamentPair.winner)
        )
        .options(
            joinedload(Tournament.pairs)
            .joinedload(TournamentPair.votes)
        )
        .filter(Tournament.tournament_id == tournament_id)
        .first()
    )
    if tournament:
        for pair in tournament.pairs:
            # Подсчитываем голоса для каждой пары
            votes = get_db_participant_votes(db, pair.pair_id)
            pair.votes_for_participant1 = votes.get(pair.participant1_id, 0)
            pair.votes_for_participant2 = votes.get(pair.participant2_id, 0) if pair.participant2_id else 0
    return tournament

def get_db_tournaments(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    type: Optional[str] = None
) -> List[Tournament]:
    """Получение списка турниров с пагинацией и фильтрацией"""
    query = db.query(Tournament)
    
    if type:
        query = query.filter(Tournament.type == type)
    
    return query.offset(skip).limit(limit).all()

def get_db_tournament_pair(db: Session, pair_id: int) -> Optional[TournamentPair]:
    """Получение пары по ID"""
    return db.query(TournamentPair).filter(TournamentPair.pair_id == pair_id).first()

def get_db_tournament_vote(db: Session, pair_id: int, user_id: int) -> Optional[TournamentVote]:
    """Проверка, голосовал ли пользователь за пару"""
    return db.query(TournamentVote).filter(
        TournamentVote.pair_id == pair_id,
        TournamentVote.user_id == user_id
    ).first()

def get_db_participant_votes(db: Session, pair_id: int) -> dict:
    """Получение количества голосов для каждого участника в паре"""
    votes = db.query(
        TournamentVote.voted_for,
        func.count(TournamentVote.voted_for).label('count')
    ).filter(
        TournamentVote.pair_id == pair_id
    ).group_by(TournamentVote.voted_for).all()
    
    return {voted_for: count for voted_for, count in votes}

def get_db_current_stage_pairs(db: Session, tournament_id: int) -> List[TournamentPair]:
    """Получение всех пар текущей стадии турнира"""
    tournament = get_db_tournament(db, tournament_id)
    if not tournament:
        return []
    
    return db.query(TournamentPair).filter(
        TournamentPair.tournament_id == tournament_id,
        TournamentPair.stage == tournament.current_stage
    ).all()

def create_db_tournament_vote(db: Session, pair_id: int, user_id: int, voted_for: int) -> TournamentVote:
    """Создание голоса за участника в паре"""
    vote = TournamentVote(
        pair_id=pair_id,
        user_id=user_id,
        voted_for=voted_for
    )
    db.add(vote)
    db.commit()
    db.refresh(vote)
    return vote

def get_db_tournament_pair_with_details(db: Session, pair_id: int) -> Optional[TournamentPair]:
    """Получение пары по ID с полной информацией об участниках и голосах"""
    pair = (
        db.query(TournamentPair)
        .options(
            joinedload(TournamentPair.participant1)
        )
        .options(
            joinedload(TournamentPair.participant2)
        )
        .options(
            joinedload(TournamentPair.winner)
        )
        .options(
            joinedload(TournamentPair.votes)
        )
        .filter(TournamentPair.pair_id == pair_id)
        .first()
    )
    if pair:
        # Подсчитываем голоса для каждой пары
        votes = get_db_participant_votes(db, pair.pair_id)
        pair.votes_for_participant1 = votes.get(pair.participant1_id, 0)
        pair.votes_for_participant2 = votes.get(pair.participant2_id, 0) if pair.participant2_id else 0
    return pair
