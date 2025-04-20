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

    # Связь с фотографией лица
    face_photo = relationship("Photo", foreign_keys=[face_photo_id], back_populates="minifigures")
    # Связь с фотографиями минифигурок
    photos = relationship("Photo", back_populates="minifigure", foreign_keys="Photo.minifigure_id")
    # Обратная связь с тегами определена в модели Tag через backref="tag_items"