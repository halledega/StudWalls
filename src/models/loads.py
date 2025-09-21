"""
This module defines the SQLAlchemy model for loads, which represent the forces
acting on the structure.
"""
from sqlalchemy import Column, Integer, String, Float
from src.core.database import Base
from enum import Enum

class LoadCase(Enum):
    """
    Enumeration for standard load case types as defined in building codes.

    This provides a controlled vocabulary for load cases, preventing typos and
    ensuring consistency.
    """
    Dead = 0
    Live = 1
    Snow = 2
    Wind = 3
    Seismic = 4
    Partition = 5

class Load(Base):
    """
    Represents a single load entity in the database.

    This SQLAlchemy model maps to the 'loads' table. Each instance represents a
    specific type of load with a name, a case (e.g., Dead, Live), a value,
    and a type (e.g., Area load).

    Attributes:
        id (int): The primary key for the load.
        name (str): A descriptive name for the load (e.g., "Roof Dead Load").
        case (str): The load case category (e.g., "Dead", "Live", "Snow").
                    This is used for grouping loads in combinations.
        value (float): The magnitude of the load (e.g., in kPa or psf).
        load_type (str): The type of load, e.g., "Area", "Point", "Line".
    """
    __tablename__ = 'loads'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    case = Column(String)
    value = Column(Float)
    load_type = Column(String)

    def __repr__(self):
        """Provides a developer-friendly string representation of the object."""
        return f"<Load(name='{self.name}', case='{self.case}', value={self.value})>"