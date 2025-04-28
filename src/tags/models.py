# src/tags/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.database import Base
import enum

class TagType(enum.Enum):
    set = "set"
    minifigure = "minifigure"
    both = "both"

class Tag(Base):
    __tablename__ = "tags"

    tag_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    tag_type = Column(Enum(TagType), nullable=False)

    # Связь с наборами через Set_Tags, синхронизирована с моделью Set
    sets = relationship("Set", secondary="set_tags", back_populates="tags")
    # Связь с минифигурками через Minifigure_Tags, синхронизирована с моделью Minifigure
    minifigures = relationship("Minifigure", secondary="minifigure_tags", back_populates="tags")

class SetTag(Base):
    __tablename__ = "set_tags"

    set_id = Column(Integer, ForeignKey("sets.set_id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.tag_id", ondelete="CASCADE"), primary_key=True)

class MinifigureTag(Base):
    __tablename__ = "minifigure_tags"

    minifigure_id = Column(String, ForeignKey("minifigures.minifigure_id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.tag_id", ondelete="CASCADE"), primary_key=True)