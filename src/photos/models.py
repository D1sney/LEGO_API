# src/photos/models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

class Photo(Base):
    __tablename__ = "photos"

    photo_id = Column(Integer, primary_key=True, index=True)
    set_id = Column(Integer, ForeignKey("sets.set_id", ondelete="CASCADE"), nullable=True)
    minifigure_id = Column(String, ForeignKey("minifigures.minifigure_id", ondelete="CASCADE"), nullable=True)
    photo_url = Column(String, nullable=False)
    is_main = Column(Boolean, default=False)

    # Связи для фотографий, которые относятся к наборам или минифигуркам
    set = relationship("Set", foreign_keys=[set_id], back_populates="photos")
    minifigure = relationship("Minifigure", foreign_keys=[minifigure_id], back_populates="photos")
    
    # Обратные связи для face_photo (главная фотография набора/минифигурки)
    sets = relationship("Set", foreign_keys="Set.face_photo_id", back_populates="face_photo")
    minifigures = relationship("Minifigure", foreign_keys="Minifigure.face_photo_id", back_populates="face_photo")