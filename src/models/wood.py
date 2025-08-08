"""
This module defines the base class for wood materials.
"""

class Wood:
    """
    Represents a wood material with its associated engineering properties.

    This class serves as a base for specific types of wood products, storing
    common properties derived from standards like CSA O86.

    Parameters
    ----------
    **kwargs : dict
        A dictionary of material properties. Expected keys include:
        'Species', 'Grade', 'fb', 'fv', 'fc', 'fcp', 'ft', 'E', 'E05', 'Type'.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initializes the Wood object with properties from keyword arguments.
        """
        self._name: str = ""
        self._species: str = kwargs.get('Species', '')
        self._grade: str = kwargs.get('Grade', '')
        self._fb: float = kwargs.get('fb', 0.0)
        self._fv: float = kwargs.get('fv', 0.0)
        self._fc: float = kwargs.get('fc', 0.0)
        self._fcp: float = kwargs.get('fcp', 0.0)
        self._ft: float = kwargs.get('ft', 0.0)
        self._E: float = kwargs.get('E', 0.0)
        self._E05: float = kwargs.get('E05', 0.0)
        self._material_type: str = kwargs.get('Type', '')

    @property
    def species(self) -> str:
        """The species of the wood (e.g., 'Spruce-Pine-Fir')."""
        return self._species

    @species.setter
    def species(self, value: str) -> None:
        self._species = value

    @property
    def grade(self) -> str:
        """The grade of the wood (e.g., 'No.1/No.2')."""
        return self._grade

    @grade.setter
    def grade(self, value: str) -> None:
        self._grade = value

    @property
    def name(self) -> str:
        """A generated short name for the material (e.g., 'SPF No.1/No.2')."""
        species_short = {
            "Douglas Fir-Larch": "D.Fir.",
            "Hem-Fir": "H.Fir.",
            "Spruce-Pine-Fir": "SPF",
            "Northern Species": "Northern"
        }
        self._name = f"{species_short.get(self._species, self._species)} {self._grade}"
        return self._name

    @property
    def fb(self) -> float:
        """Specified bending strength (Fb) in MPa."""
        return self._fb

    @fb.setter
    def fb(self, value: float) -> None:
        self._fb = value

    @property
    def fv(self) -> float:
        """Specified shear strength (Fv) in MPa."""
        return self._fv

    @fv.setter
    def fv(self, value: float) -> None:
        self._fv = value

    @property
    def fc(self) -> float:
        """Specified compressive strength parallel to grain (Fc) in MPa."""
        return self._fc

    @fc.setter
    def fc(self, value: float) -> None:
        self._fc = value

    @property
    def fcp(self) -> float:
        """Specified compressive strength perpendicular to grain (Fcp) in MPa."""
        return self._fcp

    @fcp.setter
    def fcp(self, value: float) -> None:
        self._fcp = value

    @property
    def ft(self) -> float:
        """Specified tensile strength parallel to grain (Ft) in MPa."""
        return self._ft

    @ft.setter
    def ft(self, value: float) -> None:
        self._ft = value

    @property
    def E(self) -> float:
        """Modulus of Elasticity (E) in MPa."""
        return self._E

    @E.setter
    def E(self, value: float) -> None:
        self._E = value

    @property
    def E05(self) -> float:
        """Fifth percentile Modulus of Elasticity (E05) in MPa."""
        return self._E05

    @E05.setter
    def E05(self, value: float) -> None:
        self._E05 = value

    @property
    def material_type(self) -> str:
        """The type of material (e.g., 'Sawn', 'MSR', 'MEL')."""
        return self._material_type

    @material_type.setter
    def material_type(self, value: str) -> None:
        self._material_type = value
    
    