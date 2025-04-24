# src/sets/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

class Set(Base):
    __tablename__ = "sets"

    set_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    piece_count = Column(Integer, nullable=False)
    release_year = Column(Integer, nullable=False)
    theme = Column(String, nullable=False)
    sub_theme = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    face_photo_id = Column(Integer, ForeignKey("photos.photo_id"), nullable=True)

    # Связь с фотографией
    face_photo = relationship("Photo", foreign_keys=[face_photo_id], back_populates="sets")
    # Связь с минифигурками через Set_Minifigures
    minifigures = relationship("Minifigure", secondary="set_minifigures", backref="sets")
    # Связь с фотографиями наборов
    photos = relationship("Photo", back_populates="set", foreign_keys="Photo.set_id")
    # Явная связь с тегами через set_tags
    tags = relationship("Tag", secondary="set_tags", back_populates="sets")

class SetMinifigure(Base):
    __tablename__ = "set_minifigures"

    set_id = Column(Integer, ForeignKey("sets.set_id"), primary_key=True)
    minifigure_id = Column(String, ForeignKey("minifigures.minifigure_id"), primary_key=True)