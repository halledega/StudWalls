"""
This module defines the SQLAlchemy model for a story.
"""

from sqlalchemy import Column, Integer, String, Float
from src.core.database import Base

class Story(Base):
    """
    Represents a story in the database.
    """
    __tablename__ = 'stories'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    height = Column(Float)
    floor_thickness = Column(Float)

    def __repr__(self):
        return f"<Story(name='{self.name}', height={self.height})>"

