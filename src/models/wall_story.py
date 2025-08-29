from sqlalchemy import Column, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from src.core.database import Base

wall_story_loads_left_association = Table('wall_story_loads_left_association', Base.metadata,
    Column('wall_story_id', Integer, ForeignKey('wall_stories.id')),
    Column('load_id', Integer, ForeignKey('loads.id'))
)

wall_story_loads_right_association = Table('wall_story_loads_right_association', Base.metadata,
    Column('wall_story_id', Integer, ForeignKey('wall_stories.id')),
    Column('load_id', Integer, ForeignKey('loads.id'))
)

class WallStory(Base):
    __tablename__ = 'wall_stories'
    id = Column(Integer, primary_key=True)
    wall_id = Column(Integer, ForeignKey('walls.id'))
    story_id = Column(Integer, ForeignKey('stories.id'))
    wall = relationship("Wall", back_populates="stories")
    story = relationship("Story")
    loads_left = relationship("Load", secondary=wall_story_loads_left_association, cascade="all")
    loads_right = relationship("Load", secondary=wall_story_loads_right_association, cascade="all")
