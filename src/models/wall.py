"""
This module defines the SQLAlchemy model for a wall.
"""

from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.orm import relationship
from src.core.database import Base

class Wall(Base):
    """
    Represents a wall in the database.
    """
    __tablename__ = 'walls'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    length = Column(Float)
    sw = Column(Float) # self-weight

    tribs = Column(JSON)
    lu = Column(JSON)

    stories = relationship("WallStory", back_populates="wall", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Wall(name='{self.name}')>"

