"""
This module defines the unit system handling for the application, including
a unit enumeration and a conversion helper class.

It provides a centralized mechanism for converting between the internal, consistent
metric system used for all calculations and the user-facing display system, which
can be either Metric or Imperial.
"""
from enum import Enum

class Units(Enum):
    """
    Enumeration for the available unit systems.
    This provides a clear, readable way to specify the unit system throughout the app.
    """
    Metric = 0
    Imperial = 1

class UnitSystem:
    """
    Manages unit conversions and labels for the application.

    This class provides a centralized way to handle conversions between the
    internal (Metric) and display (Imperial or Metric) unit systems. It uses
    a dictionary of conversion factors for various physical quantities.

    Attributes:
        system (Units): The active unit system for display and input.
    """

    # The _CONVERSIONS dictionary is the core of this class. It stores the
    # fundamental information needed for conversions.
    # Format: 'quantity_type': ('metric_unit_symbol', 'imperial_unit_symbol', to_metric_factor)
    _CONVERSIONS = {
        # quantity: (metric_unit, imperial_unit, to_metric_factor)
        'pressure': ('kPa', 'psf', 0.04788),      # pounds per square foot to kilopascals
        'udl': ('kN/m', 'plf', 0.01459),          # pounds per linear foot to kilonewtons per meter
        'load': ('kN', 'lb', 4.448222 / 1000),    # pounds to kilonewtons
        'length_ft_m': ('m', 'ft', 1 / 3.28084),  # feet to meters
        'length_ft_mm': ('mm', 'ft', 304.8),      # feet to millimeters
        'length_in_mm': ('mm', 'in', 25.4),       # inches to millimeters
    }

    def __init__(self, system: Units):
        """
        Initializes the UnitSystem.

        Args:
            system (Units): The desired unit system for display and input (Metric or Imperial).
        """
        self.system = system

    def to_metric(self, value: float, quantity: str) -> float:
        """
        Converts a value from the current display unit system to the internal metric system.

        If the current system is Imperial, the value is multiplied by the
        appropriate conversion factor. If the system is already Metric, the value
        is returned unchanged.

        Args:
            value (float): The numeric value to convert.
            quantity (str): The type of physical quantity (e.g., 'pressure', 'length_ft_m').
                            This key is used to look up the conversion factor.

        Returns:
            float: The converted value in the metric system.
        """
        if self.system == Units.Imperial:
            return value * self._CONVERSIONS[quantity][2]
        return value

    def from_metric(self, value: float, quantity: str) -> float:
        """
        Converts a value from the internal metric system to the current display unit system.

        If the current system is Imperial, the value is divided by the
        appropriate conversion factor. If the system is Metric, the value is
        returned unchanged.

        Args:
            value (float): The numeric value in metric to convert.
            quantity (str): The type of physical quantity (e.g., 'pressure', 'length_ft_m').

        Returns:
            float: The converted value in the display system.
        """
        if self.system == Units.Imperial:
            return value / self._CONVERSIONS[quantity][2]
        return value

    def get_display_unit(self, quantity: str) -> str:
        """
        Gets the display unit symbol string for a given quantity type.

        Args:
            quantity (str): The type of physical quantity (e.g., 'pressure', 'length_ft_m').

        Returns:
            str: The unit symbol for the current display system (e.g., 'kPa' or 'psf').
        """
        if self.system == Units.Imperial:
            return self._CONVERSIONS[quantity][1] # Return imperial unit symbol
        return self._CONVERSIONS[quantity][0]  # Return metric unit symbol