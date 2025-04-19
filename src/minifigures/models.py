# src/minifigures/models.py
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

class Minifigure(Base):
    __tablename__ = "minifigures"

    minifigure_id = Column(String, primary_key=True, index=True)
    character_name = Column(String, nullable=False)
    name = Column(String, unique=True, nullable=False)
    face_photo_id = Column(Integer, ForeignKey("photos.photo_id"), nullable=True)

    # Связь с фотографией
    face_photo = relationship("Photo", foreign_keys=[face_photo_id], back_populates="minifigures")
    # Связь с наборами через Set_Minifigures
    sets = relationship("Set", secondary="set_minifigures", back_populates="minifigures")
    # Связь с тегами через Minifigure_Tags
    tags = relationship("Tag", secondary="minifigure_tags", back_populates="minifigures")