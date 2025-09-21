"""
This module defines the SQLAlchemy model for a load combination.

A load combination is a named collection of load cases, each with a specific
multiplier (factor), used to determine the total factored load on a structure
for design purposes (e.g., 1.25*Dead Load + 1.5*Live Load).
"""

from sqlalchemy import Column, Integer, String, event
from sqlalchemy.orm import relationship
from ..core.database import Base
from .load_combination_item import LoadCombinationItem

class LoadCombination(Base):
    """
    Represents a single load combination in the database.

    This class is a SQLAlchemy model that maps to the 'load_combinations' table.
    It holds the name of the combination and establishes a relationship to the
    individual factored loads that make up the combination.

    Attributes:
        id (int): The primary key for the load combination.
        name (str): The unique name for the load combination (e.g., "1.4D").
        items (relationship): A one-to-many relationship to LoadCombinationItem objects.
                              This allows access to all the factored loads associated
                              with this combination. The `cascade="all, delete-orphan"`
                              ensures that when a LoadCombination is deleted, all its
                              associated items are also deleted from the database.
    """
    __tablename__ = 'load_combinations'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    # This relationship links a LoadCombination to its constituent parts (the items).
    # `backref="load_combination"` creates a convenient attribute on the LoadCombinationItem
    # model to refer back to its parent LoadCombination.
    # `cascade="all, delete-orphan"` is crucial for data integrity. It means that if a
    # LoadCombination record is deleted, all of its child LoadCombinationItem records
    # will be automatically deleted as well.
    items = relationship("LoadCombinationItem", backref="load_combination", cascade="all, delete-orphan")

    def add_item(self, load, factor):
        """
        A helper method to create and add a new LoadCombinationItem to this combination.

        Args:
            load (Load): The Load object to be included in the combination.
            factor (float): The multiplication factor for this load.
        """
        item = LoadCombinationItem(load=load, factor=factor)
        self.items.append(item)

    def __repr__(self):
        """Provides a developer-friendly string representation of the object."""
        return f"<LoadCombination(name='{self.name}')>"