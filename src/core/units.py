"""
This module defines the unit system handling for the application,
including unit enumerations and a conversion helper class.
"""
from enum import Enum

class Units(Enum):
    """Enumeration for the available unit systems."""
    Metric = 0
    Imperial = 1

class UnitSystem:
    """
    Manages unit conversions and labels for the application.

    This class provides a centralized way to handle conversions between the
    internal (Metric) and display (Imperial or Metric) unit systems. It uses
    a dictionary of conversion factors for various physical quantities.

    Attributes
    ----------
    system : Units
        The active unit system for display and input.
    """

    _CONVERSIONS = {
        # quantity: (metric_unit, imperial_unit, to_metric_factor)
        'pressure': ('kPa', 'psf', 0.04788),      # psf to kPa
        'udl': ('kN/m', 'plf', 0.01459),          # plf to kN/m
        'load': ('kN', 'lb', 4.448222 / 1000),    # lb to kN
        'length_ft_m': ('m', 'ft', 1 / 3.28084),  # ft to m
        'length_ft_mm': ('mm', 'ft', 304.8),      # ft to mm
        'length_in_mm': ('mm', 'in', 25.4),       # in to mm
    }

    def __init__(self, system: Units):
        """
        Initializes the UnitSystem.

        Parameters
        ----------
        system : Units
            The desired unit system for display and input.
        """
        self.system = system

    def to_metric(self, value: float, quantity: str) -> float:
        """
        Converts a value from the display unit system to the internal metric system.

        If the current system is Imperial, the value is multiplied by the
        appropriate conversion factor. Otherwise, it's returned unchanged.

        Parameters
        ----------
        value : float
            The numeric value to convert.
        quantity : str
            The type of physical quantity (e.g., 'pressure', 'length_ft_m').

        Returns
        -------
        float
            The converted value in the metric system.
        """
        if self.system == Units.Imperial:
            return value * self._CONVERSIONS[quantity][2]
        return value

    def from_metric(self, value: float, quantity: str) -> float:
        """
        Converts a value from the internal metric system to the display unit system.

        If the current system is Imperial, the value is divided by the
        appropriate conversion factor. Otherwise, it's returned unchanged.

        Parameters
        ----------
        value : float
            The numeric value in metric to convert.
        quantity : str
            The type of physical quantity (e.g., 'pressure', 'length_ft_m').

        Returns
        -------
        float
            The converted value in the display system.
        """
        if self.system == Units.Imperial:
            return value / self._CONVERSIONS[quantity][2]
        return value

    def get_display_unit(self, quantity: str) -> str:
        """
        Gets the display unit string for a given quantity type.

        Parameters
        ----------
        quantity : str
            The type of physical quantity (e.g., 'pressure', 'length_ft_m').

        Returns
        -------
        str
            The unit symbol for the current display system (e.g., 'kPa' or 'psf').
        """
        if self.system == Units.Imperial:
            return self._CONVERSIONS[quantity][1]
        return self._CONVERSIONS[quantity][0]
