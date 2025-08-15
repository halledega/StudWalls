"""
This module defines the SQLAlchemy model for a wall.
"""

from sqlalchemy import Column, Integer, String, Float, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from src.core.database import Base

wall_story_association = Table('wall_story_association', Base.metadata,
    Column('wall_id', Integer, ForeignKey('walls.id')),
    Column('story_id', Integer, ForeignKey('stories.id'))
)

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
    loads_left = Column(JSON)
    loads_right = Column(JSON)
    lu = Column(JSON)

    stories = relationship("Story", secondary=wall_story_association)

    def __repr__(self):
        return f"<Wall(name='{self.name}')>"

