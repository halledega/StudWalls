"""
This module defines the SQLAlchemy model for a story or level in a building.
"""

from sqlalchemy import Column, Integer, String, Float
from src.core.database import Base

class Story(Base):
    """
    Represents a single story or level in the building model.

    This SQLAlchemy model maps to the 'stories' table. Each instance holds
    information about a specific floor level, such as its name and height.

    Attributes:
        id (int): The primary key for the story.
        name (str): A descriptive name for the story (e.g., "Ground Floor", "Roof").
        height (float): The height of the story (e.g., in meters or feet).
        floor_thickness (float): The thickness of the floor slab or structure above the story.
    """
    __tablename__ = 'stories'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    height = Column(Float)
    floor_thickness = Column(Float)

    def __repr__(self):
        """Provides a developer-friendly string representation of the object."""
        return f"<Story(name='{self.name}', height={self.height})>"