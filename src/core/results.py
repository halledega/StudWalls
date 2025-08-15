"""
This module defines the DesignResult dataclass for storing analysis results.
"""
from dataclasses import dataclass, field
from typing import Any
from ..models.section import Section
from ..models.story import Story


@dataclass
class DesignResult:
    """
    Represents the governing design solution for a single floor level.

    This dataclass stores all necessary information about the most efficient
    stud configuration (size, spacing, plys) that satisfies all load
    combinations for a specific floor. It includes the governing (worst-case)
    design capacity ratio, the load combination that caused it, and the
    detailed factored loads and resistances.

    Attributes
    ----------
    level : int
        The floor level number this result applies to (e.g., 1, 2, 3).
    story : Story | None
        The Story object representing the story this result applies to.
    stud : Section | None
        The Section object representing the stud used in the design.
    spacing : float
        The on-center spacing of the studs, in millimeters (mm).
    plys : int
        The number of plys used for the stud.
    dc_ratio : float
        The governing (highest) design capacity ratio (Pf / Pr).
    governing_combo : str
        The name of the load combination that resulted in the highest dc_ratio.
    Pf : float
        The factored axial load (in kN) for the governing combination.
    Pr : float
        The factored compressive resistance (in kN) for the governing combination.
    k_factors : dict[str, Any]
        Modification factors used in the resistance calculation.
    wood_volume : float
        A proxy for wood volume per unit length of wall (Area / spacing).
    """
    level: int = 0
    story: Story | None = None
    stud: Section | None = None
    spacing: float = 0
    plys: int = 0
    dc_ratio: float = 0
    governing_combo: str = ""
    Pf: float = 0
    Pr: float = 0
    k_factors: dict[str, Any] = field(default_factory=dict)
    wood_volume: float = 0

