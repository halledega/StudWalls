from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from ..core.database import Base

class LoadCombination(Base):
    __tablename__ = 'load_combinations'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    factors = Column(JSON, nullable=False)

    def __repr__(self):
        return f"<LoadCombination(name='{self.name}')>"
