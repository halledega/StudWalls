from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base

class Stud(Base):
    __tablename__ = 'studs'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    section_id = Column(Integer, ForeignKey('sections.id'), nullable=False)
    material_id = Column(Integer, ForeignKey('wood_materials.id'), nullable=False)

    section = relationship("Section", back_populates="studs")
    material = relationship("Wood")

    def __repr__(self):
        return f"<Stud(name='{self.name}')>"
