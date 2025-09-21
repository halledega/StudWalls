"""
This module defines the SQLAlchemy model for a design result.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from src.core.database import Base

class Result(Base):
    """
    Represents a single design result in the database.

    This model stores the outcome of a structural analysis for a specific
    stud configuration within a single wall story. It holds all the key
    design parameters and outcomes, allowing for both a complete history of all
    valid design options and the selection of a single 'final' design.

    Attributes:
        id (int): Primary key.
        wall_story_id (int): Foreign key linking this result to a `WallStory`.
        stud_id (int): Foreign key linking to the `Section` used as a stud.
        stud (relationship): Relationship to the `Section` object.
        spacing (float): The on-center spacing of the studs (mm).
        plys (int): The number of plys used.
        dc_ratio (float): The design capacity ratio (Pf / Pr).
        governing_combo (str): The name of the governing load combination.
        Pf (float): Factored axial load (kN).
        Pr (float): Factored compressive resistance (kN).
        k_factors (JSON): JSON-encoded dictionary of modification factors (Kd, Kh, etc.).
        wood_volume (float): A proxy for wood volume, used for optimization.
        is_final (bool): A flag to mark this result as the chosen 'final' design
                         for the associated wall story. Defaults to False.
        wall_story (relationship): A many-to-one relationship back to the parent `WallStory`.
    """
    __tablename__ = 'results'

    id = Column(Integer, primary_key=True)
    wall_story_id = Column(Integer, ForeignKey('wall_stories.id'))

    stud_id = Column(Integer, ForeignKey('studs.id'))
    stud = relationship("Stud")

    spacing = Column(Float)
    plys = Column(Integer)
    dc_ratio = Column(Float)
    governing_combo = Column(String)
    Pf = Column(Float)
    Pr = Column(Float)
    k_factors = Column(JSON)
    wood_volume = Column(Float)
    is_final = Column(Boolean, default=False)

    wall_story = relationship("WallStory", back_populates="results")

    def __repr__(self):
        return f"<Result(wall_story_id={self.wall_story_id}, dc_ratio={self.dc_ratio}, is_final={self.is_final})>"
