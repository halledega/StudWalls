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

    studs = relationship("Stud", back_populates="section")

    @property
    def Ag(self):
        """Gross Area"""
        return self.width * self.depth * self.plys

    @property
    def Ix(self):
        """Moment of Inertia about the strong axis"""
        return (self.plys * self.width) * (self.depth ** 3) / 12

    @property
    def Iy(self):
        """Moment of Inertia about the weak axis"""
        return self.depth * ((self.plys * self.width) ** 3) / 12

    @property
    def Sx(self):
        """Section Modulus about the strong axis"""
        return self.Ix / (self.depth / 2)

    @property
    def Sy(self):
        """Section Modulus about the weak axis"""
        return self.Iy / ((self.plys * self.width) / 2)

    @property
    def name(self):
        return f"{self.width}x{self.depth}"

    def __repr__(self):
        return f"<Section(width={self.width}, depth={self.depth}, plys={self.plys})>"
