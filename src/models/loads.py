"""
This module defines the SQLAlchemy model for loads.
"""
from sqlalchemy import Column, Integer, String, Float
from src.core.database import Base
from enum import Enum

class LoadCase(Enum):
    """Enumeration for the available unit systems."""
    Dead = 0
    Live = 1
    Snow = 2
    Wind = 3
    Seismic = 4
    Partition = 5

class Load(Base):
    """
    Represents a load in the database.
    """
    __tablename__ = 'loads'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    case = Column(String)
    value = Column(Float)
    load_type = Column(String)

    def __repr__(self):
        return f"<Load(name='{self.name}', case='{self.case}', value={self.value})>"
