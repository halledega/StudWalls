"""
This module defines the SQLAlchemy model for a structural section.

A section represents the physical dimensions of a structural member, such as a stud.
It includes properties like width, depth, and number of plys.
"""

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base
from src.models.wood import Wood

class Section(Base):
    """
    Represents a structural cross-section in the database.

    This SQLAlchemy model maps to the 'sections' table. It stores the geometric
    properties of a member and provides calculated properties for engineering analysis.

    Attributes:
        id (int): The primary key for the section.
        width (float): The width of a single ply of the section (e.g., 38.1 mm for a 2x4).
        depth (float): The depth of the section (e.g., 88.9 mm for a 2x4).
        plys (int): The number of plys making up the full section.
        lu_width (float): The unsupported length for buckling about the weak axis.
        lu_depth (float): The unsupported length for buckling about the strong axis.
        studs (relationship): A one-to-many relationship to the Stud objects that use this section.
    """
    __tablename__ = 'sections'

    id = Column(Integer, primary_key=True)
    width = Column(Float)
    depth = Column(Float)
    plys = Column(Integer, default=1)
    lu_width = Column(Float, default=0)
    lu_depth = Column(Float, default=0)

    # This relationship links a Section to the Studs that use it.
    # `back_populates` creates a two-way relationship, so you can access the Section
    # from a Stud object via `my_stud.section`.
    studs = relationship("Stud", back_populates="section")

    @property
    def Ag(self):
        """Calculates the Gross Area of the cross-section."""
        return self.width * self.depth * self.plys

    @property
    def Ix(self):
        """Calculates the Moment of Inertia about the strong axis (X-X)."""
        return (self.plys * self.width) * (self.depth ** 3) / 12

    @property
    def Iy(self):
        """Calculates the Moment of Inertia about the weak axis (Y-Y)."""
        return self.depth * ((self.plys * self.width) ** 3) / 12

    @property
    def Sx(self):
        """Calculates the Section Modulus about the strong axis (X-X)."""
        if self.depth == 0: return 0
        return self.Ix / (self.depth / 2)

    @property
    def Sy(self):
        """Calculates the Section Modulus about the weak axis (Y-Y)."""
        if self.plys == 0 or self.width == 0: return 0
        return self.Iy / ((self.plys * self.width) / 2)

    @property
    def name(self):
        """Generates a simple name for the section based on its dimensions."""
        return f"{self.width}x{self.depth}"

    def __repr__(self):
        """Provides a developer-friendly string representation of the object."""
        return f"<Section(width={self.width}, depth={self.depth}, plys={self.plys})>"