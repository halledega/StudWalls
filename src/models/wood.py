"""
This module defines the SQLAlchemy model for wood materials.

It represents the engineering properties of different types and grades of wood.
"""

from sqlalchemy import Column, Integer, String, Float
from src.core.database import Base

class Wood(Base):
    """
    Represents a wood material and its engineering properties in the database.

    This SQLAlchemy model maps to the 'wood_materials' table. Each instance holds
    the design values (e.g., bending strength, modulus of elasticity) for a
    specific species and grade of lumber.

    Attributes:
        id (int): The primary key for the material.
        name (str): A descriptive name for the material (e.g., "SPF No.1/No.2").
        category (str): The category of the wood product (e.g., "Dimension Lumber").
        species (str): The wood species (e.g., "SPF", "Douglas Fir-Larch").
        grade (str): The grade of the lumber (e.g., "No.1/No.2", "Select Structural").
        fb (float): The specified strength in bending (Fb).
        fv (float): The specified strength in shear (Fv).
        fc (float): The specified strength in compression parallel to grain (Fc).
        fcp (float): The specified strength in compression perpendicular to grain (Fcp).
        ft (float): The specified strength in tension parallel to grain (Ft).
        E (float): The mean modulus of elasticity (E).
        E05 (float): The fifth percentile modulus of elasticity (E05), used for stability calculations.
        material_type (str): The type of material, e.g., "Sawn", "MSR", "MEL".
    """
    __tablename__ = 'wood_materials'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)
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
        """Provides a developer-friendly string representation of the object."""
        return f"<Wood(name='{self.name}', species='{self.species}', grade='{self.grade}')>"