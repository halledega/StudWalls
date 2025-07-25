from dataclasses import dataclass
from typing import Any
from ..models import Section


@dataclass
class DesignResult:
    """Represents the final design for a single floor level."""
    level: int
    stud: Section
    spacing: float  # in mm
    plys: int
    dc_ratio: float
    governing_combo: str
    details: dict[str, Any]  # The detailed dict from size_studs
    wood_volume: float
