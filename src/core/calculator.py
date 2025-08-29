import csv
from pathlib import Path

import pandas as pd


from sqlalchemy.orm import joinedload


"""
This module defines the main StudWallCalculator class for performing
stud wall design calculations.
"""
from ..models.loads import Load
from ..models.stud import Stud
from ..models.section import Section
from ..models.wood import Wood
from ..models.O86 import O86_20
from ..core.units import Units, UnitSystem
from ..core.results import DesignResult
from ..core.database import get_library_db, get_working_db


class StudWallCalculator:
    """
    A calculator for designing and analyzing wood stud walls according to CSA O86-20.

    This class handles the complete design process, including load calculation,
    load combination generation, and iterative stud sizing to find an optimal
    solution. It is designed to handle multi-story buildings and accumulates
    loads from the roof down to the foundation.

    Attributes
    ----------
    units : Units
        The unit system (Imperial or Metric) used for inputs and outputs.
    unit_system : UnitSystem
        The helper class that manages unit conversions.
    _o86 : O86_20
        An instance of the O86_20 class containing CSA O86-20 code calculations.
    final_results : dict
        A dictionary storing the final DesignResult object for each floor level.
    """

    def __init__(self, units: Units = Units.Imperial, wall: 'Wall' = None, db_session=None):
        """
        Initializes the StudWallCalculator.

        This sets up the calculator with the specified unit system, loads all
        necessary data, and initializes default design parameters.

        Parameters
        ----------
        units : Units, optional
            The unit system to be used for inputs and outputs, by default
            Units.Imperial.
        wall : Wall, optional
            The wall object to be analyzed.
        db_session : Session, optional
            The database session to be used by the calculator.
        """
        self.units = units
        self.unit_system = UnitSystem(units)
        self._o86 = O86_20
        self.final_results = {}
        self.wall = wall
        self.db_session = db_session

        self._studs = self._initialize_studs()
        self._spacings = [406, 305, 203]  # Corresponds to 16", 12", 8"

    def _initialize_studs(self):
        """
        Initializes a list of stud Section objects for common lumber sizes.
        """
        if not self.db_session:
            db = next(get_working_db())
            studs = db.query(Stud).all()
            db.close()
            return studs
        return self.db_session.query(Stud).options(
            joinedload(Stud.section),
            joinedload(Stud.material)
        ).all()


    def _calculate_loads(self):
        """
        Calculate and accumulate unfactored loads for all floors.
        """
        floors = {}
        num_stories = len(self.wall.stories)
        for i, wall_story in enumerate(self.wall.stories):
            all_loads_for_story = wall_story.loads_left + wall_story.loads_right

            dead_kpa = sum(load.value for load in all_loads_for_story if load.case.lower() == 'dead')
            live_kpa = sum(load.value for load in all_loads_for_story if load.case.lower() == 'live')
            snow_kpa = sum(load.value for load in all_loads_for_story if load.case.lower() == 'snow')
            partition_kpa = sum(load.value for load in all_loads_for_story if load.case.lower() == 'partition')

            total_trib = self.wall.tribs[i][0] + self.wall.tribs[i][1]
            if i == 0:  # Top floor (roof)
                dl = (dead_kpa * (total_trib / 1000)) + self.wall.sw
            else:  # Typical floor
                dl = (dead_kpa + partition_kpa) * (total_trib / 1000) + self.wall.sw

            ll = live_kpa * (total_trib / 1000)
            sl = snow_kpa * (total_trib / 1000)

            floors[num_stories - i] = {'DL': dl, 'LL': ll, 'SL': sl}

        floor_df = pd.DataFrame(floors).transpose()
        return floor_df.cumsum()

    def _calculate_load_combinations(self, loads_df):
        """
        Calculate factored load combinations according to building code.
        """
        combo_dict = {
            '1.4DL': loads_df['DL'] * 1.4,
            '1.25DL+1.5LL+1.0SL': loads_df['DL'] * 1.25 + loads_df['LL'] * 1.5 + loads_df['SL'] * 1.0,
            '1.25DL+1.5SL+1.0LL': loads_df['DL'] * 1.25 + loads_df['SL'] * 1.5 + loads_df['LL'] * 1.0,
            '1.25DL+1.5LL': loads_df['DL'] * 1.25 + loads_df['LL'] * 1.5,
            '1.25DL+1.5SL': loads_df['DL'] * 1.25 + loads_df['SL'] * 1.5
        }
        return pd.DataFrame(combo_dict)

    def _size_stud(self, section, material, duration, pl, ps):
        """
        Calculates the factored axial compressive resistance (Pr) of a single stud.
        """
        k_factors = {
            "Kd": self._o86.CL5_3_2_2(duration, pl, ps),
            "Kh": 1.0,
            "Kse": 1.0,
            "Ksc": 1.0,
            "Kt": 1.0,
        }
        pr_calcs = {
            'width': self._o86.CL6_5_6_2_3(section, material, section.lu_width, **k_factors),
            'depth': self._o86.CL6_5_6_2_3(section, material, section.lu_depth, **k_factors),
        }
        return pr_calcs, k_factors

    def calculate(self):
        """
        Performs the main stud wall design calculation and returns the results as formatted strings.
        """
        self.final_results = {}
        summary_output = ""
        detailed_output = ""

        loads_df = self._calculate_loads()
        detailed_output += "\nUnfactored Total Loads per floor\n"
        detailed_output += loads_df.to_string() + "\n"

        combo_df = self._calculate_load_combinations(loads_df)
        detailed_output += "\nFactored Loads Combos per floor\n"
        detailed_output += combo_df.to_string() + "\n"

        for level, wall_story in enumerate(self.wall.stories):
            h = wall_story.story.height
            load_dict = loads_df.loc[level + 1].to_dict()
            load_combo_dict = combo_df.loc[level + 1].to_dict()

            all_solutions_for_level = []

            for stud_template in self._studs:
                for spacing in self._spacings:
                    for plys in range(1, 4):
                        section = Section(
                            width=stud_template.section.width,
                            depth=stud_template.section.depth,
                            plys=plys,
                            lu_width=self.wall.lu[level][0],
                            lu_depth=self.wall.lu[level][1]
                        )

                        governing_result_for_design = DesignResult(level=level, story=wall_story.story, stud=stud_template, spacing=spacing, plys=plys)
                        max_dc_ratio = 0
                        governing_combo = None

                        for combo, load in load_combo_dict.items():
                            if combo == '1.4DL':
                                duration, long, short = 'Long', 0, 0
                            elif combo == '1.25DL+1.5LL+1.0SL':
                                duration, long, short = 'Standard', load_dict['DL'], load_dict['LL'] + 0.5 * load_dict['SL']
                            elif combo == '1.25DL+1.5SL+1.0LL':
                                duration, long, short = 'Standard', load_dict['DL'], load_dict['SL'] + 0.5 * load_dict['LL']
                            elif combo == '1.25DL+1.5LL':
                                duration, long, short = 'Standard', load_dict['DL'], load_dict['LL']
                            elif combo == '1.25DL+1.5SL':
                                duration, long, short = 'Standard', load_dict['DL'], load_dict['SL']

                            pf = load * (spacing / 1000)
                            pl = long * (spacing / 1000)
                            ps = short * (spacing / 1000)

                            pr_calcs, k_factors = self._size_stud(section, stud_template.material, duration, pl, ps)
                            pr = min(pr_calcs['width']['Pr'], pr_calcs['depth']['Pr']) / 1000
                            dc = pf / pr if pr > 0 else float('inf')

                            if dc > max_dc_ratio:
                                max_dc_ratio = dc
                                governing_combo = combo
                                governing_result_for_design.Pf = pf
                                governing_result_for_design.Pr = pr
                                governing_result_for_design.k_factors = k_factors

                        governing_result_for_design.dc_ratio = max_dc_ratio
                        governing_result_for_design.governing_combo = governing_combo
                        governing_result_for_design.wood_volume = section.Ag / spacing
                        all_solutions_for_level.append(governing_result_for_design)

            detailed_output += "\n---------------------------------------------------------\n"
            detailed_output += f"All Design Options for Level {level + 1}\n"

            all_solutions_for_level.sort(key=lambda x: (x.stud.section.depth, x.plys, x.spacing))

            summary_list = []
            for result in all_solutions_for_level:
                display_spacing = self.unit_system.from_metric(result.spacing, 'length_in_mm')
                spacing_unit = self.unit_system.get_display_unit('length_in_mm')
                status = "Pass" if result.dc_ratio < 1.0 else "Fail"
                summary_list.append({
                    "Stud": f"({result.plys})-{result.stud.name}",
                    "Spacing": f"{display_spacing:.0f} {spacing_unit} o/c",
                    "Wood Volume": f"{result.wood_volume:.2f}",
                    "DC Ratio": f"{result.dc_ratio:.2f}",
                    "Status": status
                })
            summary_df = pd.DataFrame(summary_list)
            detailed_output += summary_df.to_string() + "\n"

            valid_solutions = [s for s in all_solutions_for_level if s.dc_ratio < 1.0]

            if not valid_solutions:
                summary_output += f"Level {level + 1}: No adequate design found.\n"
                detailed_output += "\nNo adequate design found.\n"
                self.final_results[level] = DesignResult(level=level, story=wall_story.story, stud=None)
            else:
                optimal_solution = sorted(valid_solutions, key=lambda x: x.wood_volume)[0]
                self.final_results[level] = optimal_solution

                display_spacing = self.unit_system.from_metric(optimal_solution.spacing, 'length_in_mm')
                spacing_unit = self.unit_system.get_display_unit('length_in_mm')
                display_pf = self.unit_system.from_metric(optimal_solution.Pf, 'load')
                display_pr = self.unit_system.from_metric(optimal_solution.Pr, 'load')
                load_unit = self.unit_system.get_display_unit('load')

                summary_output += f"--- Level {level + 1} ---\n"
                summary_output += f"  Stud: ({optimal_solution.plys})-{optimal_solution.stud.name}\n"
                summary_output += f"  Spacing: {display_spacing:.0f} {spacing_unit} o/c\n"
                summary_output += f"  DC Ratio: {optimal_solution.dc_ratio:.2f}\n\n"

                final_data = {
                    "Parameter": [
                        "Stud", "Material", "Spacing", "Governing Combo",
                        "Factored Load (Pf)", "Factored Resistance (Pr)",
                        "DC Ratio", "Wood Volume Proxy"
                    ],
                    "Value": [
                        f"({optimal_solution.plys})-{optimal_solution.stud.name}",
                        optimal_solution.stud.material.name,
                        f"{display_spacing:.0f} {spacing_unit} o/c",
                        optimal_solution.governing_combo,
                        f"{display_pf:.2f} {load_unit}",
                        f"{display_pr:.2f} {load_unit}",
                        f"{optimal_solution.dc_ratio:.2f}",
                        f"{optimal_solution.wood_volume:.2f} mm"
                    ]
                }
                final_df = pd.DataFrame(final_data).set_index('Parameter')

                detailed_output += "\n---------------------------------------------------------\n"
                detailed_output += f"Final (Optimal) Design for Level {level + 1}\n"
                detailed_output += final_df.to_string() + "\n"

            detailed_output += "---------------------------------------------------------\n\n"

        return summary_output, detailed_output

    def get_results(self):
        return self.final_results