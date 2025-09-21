"""
This module defines the SQLAlchemy model for a stud.

A stud is a structural member composed of a specific cross-section and material.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base

class Stud(Base):
    """
    Represents a stud type in the database.

    This SQLAlchemy model maps to the 'studs' table. It links together a
    `Section` and a `Wood` material to define a complete structural member.

    Attributes:
        id (int): The primary key for the stud.
        name (str): A unique, descriptive name for the stud type (e.g., "2x6 SPF No.1/No.2").
        section_id (int): A foreign key referencing the `sections.id`.
        material_id (int): A foreign key referencing the `wood_materials.id`.
        section (relationship): A many-to-one relationship to the `Section` object.
                                This provides access to the stud's physical dimensions.
        material (relationship): A many-to-one relationship to the `Wood` object.
                                 This provides access to the stud's material properties.
    """
    __tablename__ = 'studs'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    
    # Foreign key to the Section table
    section_id = Column(Integer, ForeignKey('sections.id'), nullable=False)
    # Foreign key to the Wood material table
    material_id = Column(Integer, ForeignKey('wood_materials.id'), nullable=False)

    # This relationship allows you to access the full Section object from a Stud
    # instance via `my_stud.section`.
    # `back_populates="studs"` creates a two-way link with the Section model.
    section = relationship("Section", back_populates="studs")
    
    # This relationship allows you to access the full Wood object from a Stud
    # instance via `my_stud.material`.
    material = relationship("Wood")

    def __repr__(self):
        """Provides a developer-friendly string representation of the object."""
        return f"<Stud(name='{self.name}')>"
