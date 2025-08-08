"""
This module contains static methods for calculations based on the CSA O86-20 standard.
"""
from .section import Section
from math import sqrt, log10

class O86_20:
    """
    A collection of static methods implementing clauses from the CSA O86-20
    standard for wood design in Canada.
    """

    @staticmethod
    def CL5_3_2_2(Duration: str = 'Standard', Pl: float = 0, Ps: float = 0) -> float:
        """
        Calculates the load duration factor (Kd) based on CSA O86-20 Clause 5.3.2.2.

        Parameters
        ----------
        Duration : str, optional
            The load duration category ('Long', 'Standard', 'Short'),
            by default 'Standard'.
        Pl : float, optional
            The long-term component of a specified load, by default 0.
        Ps : float, optional
            The short-term component of a specified load, by default 0.

        Returns
        -------
        float
            The load duration factor (Kd).
        """
        if Pl > Ps > 0:
            return O86_20.CL5_3_2_3(Pl, Ps)
        elif Pl > Ps and Ps == 0:
            return 0.65
        elif Duration == 'Short':
            return 1.15
        elif Duration == 'Standard':
            return 1.0
        elif Duration == 'Long':
            return 0.65
        return 1.0  # Default case

    @staticmethod
    def CL5_3_2_3(Pl: float, Ps: float) -> float:
        """
        Calculates Kd for combined long and short term loads, per CSA O86-20 Clause 5.3.2.3.

        Parameters
        ----------
        Pl : float
            The long-term component of a specified load.
        Ps : float
            The short-term component of a specified load.

        Returns
        -------
        float
            The calculated load duration factor (Kd).
        """
        if Pl <= 0 or Ps <= 0:
            return 1.0
        return min(1.0, max(1.0 - 0.5 * log10(Pl / Ps), 0.65))

    @staticmethod
    def CL6_5_6_2_2(h: float, b: float) -> float:
        """
        Calculates the slenderness ratio (Cc) for a rectangular cross-section.
        Based on CSA O86-20 Clause 6.5.6.2.2.

        Parameters
        ----------
        h : float
            Effective length of the member.
        b : float
            Width of the compression member.

        Returns
        -------
        float
            The slenderness ratio (Cc).
        """
        if b == 0:
            return 0
        return h / b

    @staticmethod
    def CL6_5_6_2_3(section: Section, Lu: float, **kwargs) -> dict[str, float]:
        """
        Calculates factored compressive resistance parallel to grain (Pr).
        Based on CSA O86-20 Clause 6.5.6.2.3.

        Parameters
        ----------
        section : Section
            The cross-section object of the member.
        Lu : float
            The unsupported length of the member.
        **kwargs : dict
            Modification factors (Kd, Kh, Kse, Ksc, Kt).

        Returns
        -------
        dict[str, float]
            A dictionary containing the factored resistance (Pr) and other
            intermediate calculation values.
        """
        phi = 0.8  # for sawn lumber
        Kd = kwargs.get('Kd', 1.0)
        Kh = kwargs.get('Kh', 1.0)
        Kse = kwargs.get('Kse', 1.0)
        Ksc = kwargs.get('Ksc', 1.0)
        Kt = kwargs.get('Kt', 1.0)

        design_area = section.area

        mat_type = section.material.material_type
        if mat_type == 'MSR':
            E05 = 0.85 * section.material.E05
        elif mat_type == 'MEL':
            E05 = 0.75 * section.material.E05
        else:
            E05 = section.material.E05

        Cc = O86_20.CL6_5_6_2_2(Lu, section.depth)
        Fc = section.material.fc * (Kd * Kh * Ksc * Kt)

        Kzc = min(6.3 * (section.depth * Lu) ** -0.13, 1.3) if section.depth * Lu > 0 else 1.3
        
        # Avoid division by zero if E05 is zero
        if E05 == 0:
            Kc = 0.0
        else:
            Kc = (1.0 + (Fc * Kzc * Cc ** 3) / (35 * E05 * Kse * Kt)) ** -1

        if Cc > 50:
            Pr = 0.0
        else:
            Pr = phi * Fc * design_area * Kc * Kzc

        return {'Pr': Pr, "Fc": Fc, "Kzc": Kzc, "Kc": Kc, 'Cc': Cc}

    # methods below are for spaced compression members
    @staticmethod
    def CLA6_5_6_3_7(Cc: float, section: Section, **kwargs) -> tuple[float, float]:
        """Calculates Kc for spaced compression members."""
        Fc = kwargs['Fc']
        Kse = kwargs['Kse']
        Ke = kwargs['Ke']
        Kt = kwargs['Kt']

        mat_type = section.material.material_type
        if mat_type in ("Sawn", "MSR", "MEL"):
            phi = 0.8
            k = 1.8
        else:
            phi = 0.9
            k = 2.0

        if mat_type == 'MSR':
            E05 = 0.85 * section.material.E05
        elif mat_type == 'MEL':
            E05 = 0.75 * section.material.E05
        else:
            E05 = section.material.E05

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
    def CLA6_5_6_3_6(section: Section, **kwargs) -> dict[str, float]:
        """Calculates Pr for spaced compression members."""
        Kd = kwargs['Kd']
        Ksc = kwargs['Ksc']
        Kt = kwargs['Kt']
        l = kwargs['l']

        Fc = section.material.fc * (Kd * Ksc * Kt)
        if section.depth == 0:
            Cc = 0.0
        else:
            Cc = l / section.depth

        Kzc = min(6.3 * (section.depth * l) ** -0.13, 1.3) if section.depth * l > 0 else 1.3

        phi, Kc = O86_20.CLA6_5_6_3_7(Cc, section, Fc=Fc, Kse=1.0, Ke=1.0, Kt=1.0)

        Pr = phi * Fc * section.area * Kc * Kzc

        return {'Pr': Pr, 'Fc': Fc, 'Kc': Kc, 'Kzc': Kzc}
            
    
    