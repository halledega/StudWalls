from dataclasses import dataclass, field
from typing import Any
from ..models import Section


@dataclass
class DesignResult:
    """
    Represents the final, governing design solution for a single floor level.

    This dataclass stores all the necessary information about the most efficient
    stud configuration (size, spacing, plys) that satisfies all load
    combinations for a specific floor. It includes the governing (worst-case)
    design capacity ratio, the load combination that caused it, and the
    detailed factored loads and resistances.
    """
    level: int = 0
    """The floor level number this result applies to (e.g., 1, 2, 3)."""

    stud: Section | None = None
    """The Section object representing the stud used in the design."""

    spacing: float = 0
    """The on-center spacing of the studs, stored in millimeters (mm)."""

    plys: int = 0
    """The number of plys used for the stud."""

    dc_ratio: float = 0
    """
    The governing (highest) design capacity ratio (Pf / Pr) found among all
    load combinations for this specific stud design.
    """

    governing_combo: str = ""
    """
    The name of the load combination that resulted in the highest dc_ratio.
    """

    Pf: float = 0
    """
    The factored axial load (in kN) on the stud for the governing load
    combination.
    """

    Pr: float = 0
    """
    The factored compressive resistance (in kN) of the stud for the governing
    load combination.
    """

    k_factors: dict[str, Any] = field(default_factory=dict)
    """
    A dictionary of the modification factors (k_factors) used in calculating
    the compressive resistance for the governing load combination.
    """

    wood_volume: float = 0
    """The cross-sectional area of the stud divided by its spacing, as a proxy for wood volume per unit length of wall."""

