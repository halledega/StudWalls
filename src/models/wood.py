"""
This module defines the SQLAlchemy model for wood materials.
"""

from sqlalchemy import Column, Integer, String, Float
from src.core.database import Base

class Wood(Base):
    """
    Represents a wood material in the database.
    """
    __tablename__ = 'wood_materials'

    id = Column(Integer, primary_key=True)
    species = Column(String)
    grade = Column(String)
    fb = Column(Float)
    fv = Column(Float)
    fc = Column(Float)
    fcp = Column(Float)
    ft = Column(Float)
    E = Column(Float)
    E05 = Column(Float)
    material_type = Column(String)

    def __repr__(self):
        return f"<Wood(species='{self.species}', grade='{self.grade}')>"

    
    