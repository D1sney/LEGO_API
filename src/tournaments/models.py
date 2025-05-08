# src/tournaments/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database import Base
from datetime import datetime

class Tournament(Base):
    __tablename__ = "tournaments"

    tournament_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)
    current_stage = Column(String, nullable=False)
    stage_deadline = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Связи
    participants = relationship("TournamentParticipant", back_populates="tournament", cascade="all, delete-orphan")
    pairs = relationship("TournamentPair", back_populates="tournament", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("type IN ('sets', 'minifigures')"),
    )

class TournamentParticipant(Base):
    __tablename__ = "tournament_participants"

    participant_id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament_id", ondelete="CASCADE"), nullable=False)
    set_id = Column(Integer, ForeignKey("sets.set_id", ondelete="CASCADE"), nullable=True)
    minifigure_id = Column(String, ForeignKey("minifigures.minifigure_id", ondelete="CASCADE"), nullable=True)
    position = Column(Integer, nullable=False)

    # Связи
    tournament = relationship("Tournament", back_populates="participants")
    set = relationship("Set", back_populates="tournament_participants")
    minifigure = relationship("Minifigure", back_populates="tournament_participants")

    __table_args__ = (
        UniqueConstraint("tournament_id", "set_id", "minifigure_id"),
        CheckConstraint("(set_id IS NOT NULL AND minifigure_id IS NULL) OR (set_id IS NULL AND minifigure_id IS NOT NULL)"),
    )

class TournamentPair(Base):
    __tablename__ = "tournament_pairs"

    pair_id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament_id", ondelete="CASCADE"), nullable=False)
    stage = Column(String, nullable=False)
    participant1_id = Column(Integer, ForeignKey("tournament_participants.participant_id", ondelete="CASCADE"), nullable=False)
    participant2_id = Column(Integer, ForeignKey("tournament_participants.participant_id", ondelete="CASCADE"), nullable=True)
    winner_id = Column(Integer, ForeignKey("tournament_participants.participant_id", ondelete="SET NULL"), nullable=True)

    # Связи
    tournament = relationship("Tournament", back_populates="pairs")
    participant1 = relationship("TournamentParticipant", foreign_keys=[participant1_id])
    participant2 = relationship("TournamentParticipant", foreign_keys=[participant2_id])
    winner = relationship("TournamentParticipant", foreign_keys=[winner_id])
    votes = relationship("TournamentVote", back_populates="pair", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("tournament_id", "stage", "participant1_id", "participant2_id"),
    )

class TournamentVote(Base):
    __tablename__ = "tournament_votes"

    vote_id = Column(Integer, primary_key=True)
    pair_id = Column(Integer, ForeignKey("tournament_pairs.pair_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    voted_for = Column(Integer, ForeignKey("tournament_participants.participant_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Связи
    pair = relationship("TournamentPair", back_populates="votes")
    user = relationship("User", back_populates="tournament_votes")
    voted_participant = relationship("TournamentParticipant")

    __table_args__ = (
        UniqueConstraint("pair_id", "user_id"),
    )