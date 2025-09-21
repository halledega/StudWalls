"""
This module defines the SQLAlchemy model for a wall.

A wall is a primary structural element in the application, composed of multiple
stories and subjected to various loads.
"""

from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.orm import relationship
from src.core.database import Base

class Wall(Base):
    """
    Represents a single wall in the database.

    This SQLAlchemy model maps to the 'walls' table. It holds the wall's name,
    physical properties, and establishes a relationship to the stories that
    make up the wall.

    Attributes:
        id (int): The primary key for the wall.
        name (str): A descriptive name for the wall.
        length (float): The length of the wall.
        sw (float): The self-weight of the wall (e.g., in kPa or psf).
        tribs (JSON): A JSON-encoded list storing tributary width data.
                      (Note: This might be refactored into a separate table in the future).
        lu (JSON): A JSON-encoded list storing unsupported length data.
                   (Note: This might be refactored into a separate table in the future).
        stories (relationship): A one-to-many relationship to WallStory objects.
                                This links the wall to its constituent stories and their loads.
                                `cascade="all, delete-orphan"` ensures that when a Wall
                                is deleted, its associated WallStory records are also deleted.
    """
    __tablename__ = 'walls'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    length = Column(Float)
    sw = Column(Float) # self-weight

    # Storing lists as JSON is a simple approach but lacks the relational integrity
    # of a proper child table. This is a potential area for future refactoring.
    tribs = Column(JSON)
    lu = Column(JSON)

    # This relationship links a Wall to its WallStory association objects.
    stories = relationship("WallStory", back_populates="wall", cascade="all, delete-orphan")

    def __repr__(self):
        """Provides a developer-friendly string representation of the object."""
        return f"<Wall(name='{self.name}')>"