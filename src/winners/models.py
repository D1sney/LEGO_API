from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database import Base
from datetime import datetime

class TournamentWinner(Base):
    __tablename__ = "tournament_winners"

    winner_id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament_id", ondelete="CASCADE"), nullable=False, unique=True)
    set_id = Column(Integer, ForeignKey("sets.set_id", ondelete="CASCADE"), nullable=True)
    minifigure_id = Column(String, ForeignKey("minifigures.minifigure_id", ondelete="CASCADE"), nullable=True)
    total_votes = Column(Integer, default=0)
    won_at = Column(DateTime(timezone=True), default=func.now())
    
    # Связи
    tournament = relationship("Tournament")
    set = relationship("Set")
    minifigure = relationship("Minifigure")
    
    __table_args__ = (
        CheckConstraint("(set_id IS NOT NULL AND minifigure_id IS NULL) OR (set_id IS NULL AND minifigure_id IS NOT NULL)"),
    ) 