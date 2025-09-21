"""
This module defines the SQLAlchemy model for a load combination item.

This model represents an individual line item within a load combination,
linking a specific load to its corresponding multiplication factor.
"""

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base

class LoadCombinationItem(Base):
    """
    Represents a single factored load within a larger LoadCombination.

    This is an association object in SQLAlchemy terms, linking a `LoadCombination`
    with a `Load` and specifying the `factor` for that relationship.

    Attributes:
        id (int): The primary key for this item.
        load_combination_id (int): A foreign key referencing the parent `load_combinations.id`.
        load_id (int): A foreign key referencing the specific `loads.id`.
        factor (float): The multiplication factor for this specific load in this combination.
        load (relationship): A many-to-one relationship to the `Load` object, allowing
                             easy access to the details of the associated load.
    """
    __tablename__ = 'load_combination_items'

    id = Column(Integer, primary_key=True)
    # Foreign key to the parent LoadCombination table
    load_combination_id = Column(Integer, ForeignKey('load_combinations.id'), nullable=False)
    # Foreign key to the Load table
    load_id = Column(Integer, ForeignKey('loads.id'), nullable=False)
    # The factor to multiply the load value by
    factor = Column(Float, nullable=False)

    # This relationship allows you to access the full Load object from a LoadCombinationItem
    # instance, for example: `my_item.load.name`
    load = relationship("Load")