from enum import Enum

class Units(Enum):
    Metric = 0
    Imperial = 1

class UnitSystem:
    """Manages unit conversions and labels for the application."""

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
        """Initializes the UnitSystem.
        
        Parameters
        ----------
        system : Units
            The desired unit system for display and input.
        """
        self.system = system

    def to_metric(self, value: float, quantity: str) -> float:
        """Converts a value from the display unit system to the internal metric system."""
        if self.system == Units.Imperial:
            return value * self._CONVERSIONS[quantity][2]
        return value

    def from_metric(self, value: float, quantity: str) -> float:
        """Converts a value from the internal metric system to the display unit system."""
        if self.system == Units.Imperial:
            return value / self._CONVERSIONS[quantity][2]
        return value

    def get_display_unit(self, quantity: str) -> str:
        """Gets the display unit string for a given quantity type."""
        if self.system == Units.Imperial:
            return self._CONVERSIONS[quantity][1]
        return self._CONVERSIONS[quantity][0]
