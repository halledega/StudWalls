"""
This module defines the SQLAlchemy model for the WallStory association object.

This object links a Wall to a Story and also holds the loads applied at that specific level.
"""

from sqlalchemy import Column, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from src.core.database import Base

# This is an association table for the many-to-many relationship between
# a WallStory and the loads applied to its left side.
wall_story_loads_left_association = Table('wall_story_loads_left_association', Base.metadata,
    Column('wall_story_id', Integer, ForeignKey('wall_stories.id')),
    Column('load_id', Integer, ForeignKey('loads.id'))
)

# This is an association table for the many-to-many relationship between
# a WallStory and the loads applied to its right side.
wall_story_loads_right_association = Table('wall_story_loads_right_association', Base.metadata,
    Column('wall_story_id', Integer, ForeignKey('wall_stories.id')),
    Column('load_id', Integer, ForeignKey('loads.id'))
)

class WallStory(Base):
    """
    Represents the association between a Wall and a Story.

    This is an association object that not only links a wall to a story but also
    carries its own data, specifically the loads applied at that level.

    Attributes:
        id (int): The primary key for this association.
        wall_id (int): Foreign key to the `walls.id`.
        story_id (int): Foreign key to the `stories.id`.
        wall (relationship): A many-to-one relationship back to the parent `Wall`.
        story (relationship): A many-to-one relationship to the associated `Story`.
        loads_left (relationship): A many-to-many relationship to `Load` objects, representing
                                 loads on the left side of the wall at this story.
        loads_right (relationship): A many-to-many relationship to `Load` objects, representing
                                  loads on the right side of the wall at this story.
        results (relationship): A one-to-many relationship to `Result` objects, storing all
                                design calculations for this wall story.
    """
    __tablename__ = 'wall_stories'
    id = Column(Integer, primary_key=True)
    wall_id = Column(Integer, ForeignKey('walls.id'))
    story_id = Column(Integer, ForeignKey('stories.id'))

    # `back_populates` creates a two-way link, allowing navigation from the Wall
    # back to its WallStory objects.
    wall = relationship("Wall", back_populates="stories")
    story = relationship("Story")

    # The `secondary` argument points to the association table defined above.
    # This setup allows a WallStory to be associated with multiple Loads, and a single
    # Load can be used in multiple WallStories.
    loads_left = relationship("Load", secondary=wall_story_loads_left_association, cascade="all")
    loads_right = relationship("Load", secondary=wall_story_loads_right_association, cascade="all")

    # This one-to-many relationship links a WallStory to all of its design results.
    # `cascade="all, delete-orphan"` ensures that when a WallStory is deleted,
    # all of its associated Result records are also deleted.
    results = relationship("Result", back_populates="wall_story", cascade="all, delete-orphan")