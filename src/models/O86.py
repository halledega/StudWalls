"""
This module contains static methods for calculations based on the CSA O86-20 standard.

The methods herein are direct implementations of the formulas and clauses
found in the Canadian wood design manual, serving as a calculation engine
for the application's core engineering logic.
"""
from .section import Section
from .wood import Wood
from math import sqrt, log10

class O86_20:
    """
    A collection of static methods implementing clauses from the CSA O86-20
    standard for wood design in Canada.

    This class is not meant to be instantiated. It acts as a namespace for
    organizing the various calculation functions related to the O86 standard,
    such as determining modification factors and member resistances.
    """

    @staticmethod
    def CL5_3_2_2(Duration: str = 'Standard', Pl: float = 0, Ps: float = 0) -> float:
        """
        Calculates the load duration factor (Kd) based on CSA O86-20 Clause 5.3.2.2.

        The load duration factor accounts for the effect of the duration of applied
        loads on the strength of wood members.

        Args:
            Duration (str, optional): The load duration category, which can be
                'Long', 'Standard', or 'Short'. Defaults to 'Standard'.
            Pl (float, optional): The long-term component of a specified load.
                Used for more detailed calculations when loads have different durations.
                Defaults to 0.
            Ps (float, optional): The short-term component of a specified load.
                Used for more detailed calculations. Defaults to 0.

        Returns:
            float: The calculated load duration factor (Kd).
        """
        if Pl > Ps > 0:
            return O86_20.CL5_3_2_3(Pl, Ps)
        elif Pl > Ps and Ps == 0:
            return 0.65  # Long-term load case
        elif Duration == 'Short':
            return 1.15
        elif Duration == 'Standard':
            return 1.0
        elif Duration == 'Long':
            return 0.65
        return 1.0  # Default case if conditions are not met

    @staticmethod
    def CL5_3_2_3(Pl: float, Ps: float) -> float:
        """
        Calculates Kd for combined long and short term loads, per CSA O86-20 Clause 5.3.2.3.

        This method is used when a load is composed of both long-term and
        short-term components.

        Args:
            Pl (float): The long-term component of a specified load.
            Ps (float): The short-term component of a specified load.

        Returns:
            float: The calculated load duration factor (Kd).
        """
        if Pl <= 0 or Ps <= 0:
            return 1.0
        # The formula from the standard, ensuring Kd does not go below 0.65 or above 1.0
        return min(1.0, max(1.0 - 0.5 * log10(Pl / Ps), 0.65))

    @staticmethod
    def CL6_5_6_2_2(h: float, b: float) -> float:
        """
        Calculates the slenderness ratio (Cc) for a rectangular cross-section.
        Based on CSA O86-20 Clause 6.5.6.2.2.

        The slenderness ratio is a measure of the member's propensity to buckle
        under compression.

        Args:
            h (float): Effective length of the member, which accounts for end conditions.
            b (float): Width of the compression member in the plane of buckling.

        Returns:
            float: The slenderness ratio (Cc).
        """
        if b == 0:
            return 0
        return h / b

    @staticmethod
    def CL6_5_6_2_3(section: Section, material: Wood, Lu: float, **kwargs) -> dict[str, float]:
        """
        Calculates factored compressive resistance parallel to grain (Pr).
        Based on CSA O86-20 Clause 6.5.6.2.3.

        This is a key calculation to determine the maximum compressive load a
        wood member can withstand.

        Args:
            section (Section): The cross-section object of the member.
            material (Wood): The material object defining the wood properties.
            Lu (float): The unsupported length of the member.
            **kwargs: A dictionary of modification factors (Kd, Kh, Kse, Ksc, Kt).

        Returns:
            dict[str, float]: A dictionary containing the factored resistance (Pr)
                              and other intermediate calculation values like Fc, Kzc, Kc, and Cc
                              for detailed reporting.
        """
        phi = 0.8  # Resistance factor for sawn lumber

        # Unpack modification factors from kwargs with defaults
        Kd = kwargs.get('Kd', 1.0)  # Load duration factor
        Kh = kwargs.get('Kh', 1.0)  # System factor
        Kse = kwargs.get('Kse', 1.0) # Service condition factor for E
        Ksc = kwargs.get('Ksc', 1.0) # Service condition factor for Fc
        Kt = kwargs.get('Kt', 1.0)  # Treatment factor

        design_area = section.Ag

        # Determine the fifth percentile modulus of elasticity (E05) based on material type
        mat_type = material.material_type
        if mat_type == 'MSR':
            E05 = 0.85 * material.E05
        elif mat_type == 'MEL':
            E05 = 0.75 * material.E05
        else: # Sawn lumber
            E05 = material.E05

        # Slenderness ratio for compression
        Cc = O86_20.CL6_5_6_2_2(Lu, section.depth)
        # Factored compressive strength parallel to grain
        Fc = material.fc * (Kd * Kh * Ksc * Kt)

        # Size factor for compressive resistance
        Kzc = min(6.3 * (section.depth * Lu) ** -0.13, 1.3) if section.depth * Lu > 0 else 1.3
        
        # Column stability factor (Kc)
        if E05 == 0:
            Kc = 0.0
        else:
            # This formula accounts for buckling failure
            Kc = (1.0 + (Fc * Kzc * Cc ** 3) / (35 * E05 * Kse * Kt)) ** -1

        # The standard imposes a maximum slenderness ratio of 50 for compression members
        if Cc > 50:
            Pr = 0.0
        else:
            Pr = phi * Fc * design_area * Kc * Kzc

        return {'Pr': Pr, "Fc": Fc, "Kzc": Kzc, "Kc": Kc, 'Cc': Cc}

    # The methods below are for spaced compression members, which are not
    # currently used in the main calculation loop but are included for completeness.
    @staticmethod
    def CLA6_5_6_3_7(Cc: float, section: Section, material: Wood, **kwargs) -> tuple[float, float]:
        """
        Calculates the column stability factor (Kc) for spaced compression members.
        (Not currently used in the primary calculation workflow).
        """
        Fc = kwargs['Fc']
        Kse = kwargs['Kse']
        Ke = kwargs['Ke']
        Kt = kwargs['Kt']

        mat_type = material.material_type
        if mat_type in ("Sawn", "MSR", "MEL"):
            phi = 0.8
            k = 1.8
        else:
            phi = 0.9
            k = 2.0

        if mat_type == 'MSR':
            E05 = 0.85 * material.E05
        elif mat_type == 'MEL':
            E05 = 0.75 * material.E05
        else:
            E05 = material.E05

        if Fc == 0:
            Ck = float('inf')
        else:
            Ck = sqrt((0.76 * E05 * Kse * Ke * Kt) / Fc)

        if Cc <= 10:
            Kc = 1.0
        elif 10 < Cc <= Ck:
            Kc = 1 - (1 / 3) * (Cc / Ck) ** 4
        elif Ck < Cc < 80:
            if Fc == 0 or k == 0:
                Kc = 0.0
            else:
                Kc = (E05 * Kse * Ke * Kt) / (k * (Cc ** 2) * Fc)
        else:
            Kc = 0.0

        return phi, Kc

    @staticmethod
    def CLA6_5_6_3_6(section: Section, material: Wood, **kwargs) -> dict[str, float]:
        """
        Calculates Pr for spaced compression members.
        (Not currently used in the primary calculation workflow).
        """
        Kd = kwargs['Kd']
        Ksc = kwargs['Ksc']
        Kt = kwargs['Kt']
        l = kwargs['l']

        Fc = material.fc * (Kd * Ksc * Kt)
        if section.depth == 0:
            Cc = 0.0
        else:
            Cc = l / section.depth

        Kzc = min(6.3 * (section.depth * l) ** -0.13, 1.3) if section.depth * l > 0 else 1.3

        phi, Kc = O86_20.CLA6_5_6_3_7(Cc, section, material, Fc=Fc, Kse=1.0, Ke=1.0, Kt=1.0)

        Pr = phi * Fc * section.Ag * Kc * Kzc

        return {'Pr': Pr, 'Fc': Fc, 'Kc': Kc, 'Kzc': Kzc}