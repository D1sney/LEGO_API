# src/photos/models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

class Photo(Base):
    __tablename__ = "photos"

    photo_id = Column(Integer, primary_key=True, index=True)
    set_id = Column(Integer, ForeignKey("sets.set_id"), nullable=True)
    minifigure_id = Column(String, ForeignKey("minifigures.minifigure_id"), nullable=True)
    photo_url = Column(String, nullable=False)
    is_main = Column(Boolean, default=False)

    # Связь с Set и Minifigure
    sets = relationship("Set", back_populates="face_photo")
    minifigures = relationship("Minifigure", back_populates="face_photo")