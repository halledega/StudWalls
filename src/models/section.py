"""
This module defines the SQLAlchemy model for a structural section.
"""

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.models.wood import Wood

class Section(Base):
    """
    Represents a structural cross-section in the database.
    """
    __tablename__ = 'sections'

    id = Column(Integer, primary_key=True)
    width = Column(Float)
    depth = Column(Float)
    plys = Column(Integer, default=1)
    lu_width = Column(Float, default=0)
    lu_depth = Column(Float, default=0)

    material_id = Column(Integer, ForeignKey('wood_materials.id'))
    material = relationship("Wood")

    @property
    def area(self):
        return self.width * self.depth * self.plys

    @property
    def name(self):
        return f"{self.width}x{self.depth}"

    def __repr__(self):
        return f"<Section(width={self.width}, depth={self.depth}, plys={self.plys})>"
