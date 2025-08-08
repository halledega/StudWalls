"""
This module defines the Section class, which represents a structural member's cross-section.
"""
from .joist_and_plank import Joist_and_Plank

class Section:
    """
    Represents a structural cross-section.

    This class holds the dimensional and material properties of a structural
    member, such as a stud.

    Parameters
    ----------
    width : float
        The width of the cross-section in millimeters.
    depth : float
        The depth of the cross-section in millimeters.
    material : Joist_and_Plank
        The material object associated with this section.
    plys : int, optional
        The number of plys for this section, by default 1.
    """

    def __init__(self, width: float, depth: float, material: Joist_and_Plank, plys: int = 1):
        self._width = width
        self._depth = depth
        self._material = material
        self._lu = {'width': 0, 'depth': 0}
        self._plys = plys

    @property
    def plys(self) -> int:
        """The number of plys for the section."""
        return self._plys

    @plys.setter
    def plys(self, value: int) -> None:
        self._plys = value

    @property
    def width(self) -> float:
        """The width of the cross-section in millimeters."""
        return self._width * self._plys

    @width.setter
    def width(self, value: float) -> None:
        self._width = value

    @property
    def depth(self) -> float:
        """The depth of the cross-section in millimeters."""
        return self._depth

    @depth.setter
    def depth(self, value: float) -> None:
        self._depth = value

    @property
    def lu(self) -> dict[str, float]:
        """The unbraced lengths ('width' and 'depth') in millimeters."""
        return self._lu

    @lu.setter
    def lu(self, value: dict[str, float]) -> None:
        self._lu['width'] = value.get('width', 0)
        self._lu['depth'] = value.get('depth', 0)

    @property
    def area(self) -> float:
        """The cross-sectional area in square millimeters."""
        return self.width * self.depth

    @property
    def material(self) -> Joist_and_Plank:
        """The material object for this section."""
        return self._material

    @property
    def name(self) -> str:
        """A string representation of the section's dimensions (e.g., '38x89')."""
        return f"{self._width}x{self._depth}"

    def __repr__(self) -> str:
        """A developer-friendly representation of the Section object."""
        return f"Section({self.width}x{self.depth}, plys={self.plys}, lu={self.lu})"