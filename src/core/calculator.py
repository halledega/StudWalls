
'''This module defines the main StudWallCalculator class, which serves as the
core engineering engine for the application. It performs all the necessary
structural analysis for a given stud wall configuration.
'''

import pandas as pd
from sqlalchemy.orm import joinedload

from ..models.loads import Load
from ..models.stud import Stud
from ..models.section import Section
from ..models.wood import Wood
from ..models.O86 import O86_20
from ..core.units import Units, UnitSystem
from ..core.results import DesignResult
from ..core.database import get_library_db, get_working_db
from ..models.load_combination import LoadCombination
from ..models.result import Result


class StudWallCalculator:
    """
    A calculator for designing and analyzing wood stud walls according to CSA O86-20.

    This class handles the complete design process, including load accumulation,
    generation of factored load combinations, and an iterative sizing process
    to find an optimal stud design. It is designed to handle multi-story buildings,
    accumulating loads from the roof down to the foundation.

    Attributes:
        units (Units): The unit system (Imperial or Metric) used for inputs and outputs.
        unit_system (UnitSystem): An instance of the helper class that manages unit conversions.
        _o86 (O86_20): A reference to the O86_20 class containing CSA O86-20 code calculations.
        final_results (dict): A dictionary storing the final DesignResult object for each floor level.
        wall (Wall): The wall object from the database to be analyzed.
        db_session (Session): The SQLAlchemy database session used for all queries.
        _studs (list[Stud]): A list of available stud types to be used in the design iteration.
        _spacings (list[float]): A list of standard stud spacings (in mm) to be tested.
    """

    def __init__(self, units: Units = Units.Imperial, wall: 'Wall' = None, db_session=None):
        """
        Initializes the StudWallCalculator.

        This sets up the calculator with the specified unit system, loads all
        necessary data from the database, and initializes default design parameters.

        Args:
            units (Units, optional): The unit system for inputs/outputs. Defaults to Units.Imperial.
            wall (Wall, optional): The wall object to be analyzed. Defaults to None.
            db_session (Session, optional): The database session. If not provided, a new one
                                           will be created. Defaults to None.
        """
        self.units = units
        self.unit_system = UnitSystem(units)
        self._o86 = O86_20
        self.final_results = {}
        self.wall = wall
        self.db_session = db_session

        self._studs = self._initialize_studs()
        self._spacings = [406, 305, 203]  # Corresponds to 16", 12", 8" in mm

    def _initialize_studs(self):
        """
        Loads all available stud definitions from the database.

        Uses `joinedload` to eagerly load the related `section` and `material` objects
        in the same query. This is a performance optimization that avoids separate
        queries for each stud's section and material later on.

        Returns:
            list[Stud]: A list of all Stud objects from the database.
        """
        if not self.db_session:
            # If no session was passed during initialization, create a temporary one.
            db = next(get_working_db())
            studs = db.query(Stud).all()
            db.close()
            return studs
        
        # Eagerly load related Section and Wood objects to prevent lazy loading N+1 problem.
        return self.db_session.query(Stud).options(
            joinedload(Stud.section),
            joinedload(Stud.material)
        ).all()


    def _calculate_loads(self) -> pd.DataFrame:
        """
        Calculates and accumulates unfactored loads for all floors of the wall.

        It iterates through each story of the wall from top to bottom, summing up
        the dead, live, and snow loads. The result is a cumulative DataFrame where
        each row represents a floor and shows the total load from all floors above.

        Returns:
            pd.DataFrame: A DataFrame with cumulative DL, LL, and SL for each floor.
        """
        floors = {}
        num_stories = len(self.wall.stories)
        for i, wall_story in enumerate(self.wall.stories):
            all_loads_for_story = wall_story.loads_left + wall_story.loads_right

            # Sum loads for the current story by case
            dead_kpa = sum(load.value for load in all_loads_for_story if load.case.lower() == 'dead')
            live_kpa = sum(load.value for load in all_loads_for_story if load.case.lower() == 'live')
            snow_kpa = sum(load.value for load in all_loads_for_story if load.case.lower() == 'snow')
            partition_kpa = sum(load.value for load in all_loads_for_story if load.case.lower() == 'partition')

            total_trib = self.wall.tribs[i][0] + self.wall.tribs[i][1]
            if i == 0:  # Top floor (roof) has no partition load from above
                dl = (dead_kpa * (total_trib / 1000)) + self.wall.sw
            else:  # Typical floor
                dl = (dead_kpa + partition_kpa) * (total_trib / 1000) + self.wall.sw

            ll = live_kpa * (total_trib / 1000)
            sl = snow_kpa * (total_trib / 1000)

            floors[num_stories - i] = {'DL': dl, 'LL': ll, 'SL': sl}

        floor_df = pd.DataFrame(floors).transpose()
        # The cumsum() is the key step for accumulating loads from the top down.
        return floor_df.cumsum()

    def _calculate_load_combinations(self, loads_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates factored load combinations based on the combinations in the database.

        Args:
            loads_df (pd.DataFrame): DataFrame of cumulative unfactored loads.

        Returns:
            pd.DataFrame: A DataFrame where columns are load combination names and
                          rows are the total factored load for each floor.
        """
        combos = self.db_session.query(LoadCombination).all()
        combo_dict = {}

        for combo in combos:
            factored_load = pd.Series([0.0] * len(loads_df), index=loads_df.index)
            for item in combo.items:
                load_case_name = item.load.case.upper()
                if load_case_name == 'DEAD':
                    factored_load += loads_df['DL'] * item.factor
                elif load_case_name == 'LIVE':
                    factored_load += loads_df['LL'] * item.factor
                elif load_case_name == 'SNOW':
                    factored_load += loads_df['SL'] * item.factor
            combo_dict[combo.name] = factored_load

        return pd.DataFrame(combo_dict)

    def _size_stud(self, section: Section, material: Wood, duration: str, pl: float, ps: float) -> tuple:
        """
        Calculates the factored axial compressive resistance (Pr) of a single stud.

        Args:
            section (Section): The stud's cross-section.
            material (Wood): The stud's material properties.
            duration (str): The load duration category ('Long', 'Standard', 'Short').
            pl (float): The long-term component of the load.
            ps (float): The short-term component of the load.

        Returns:
            tuple: A tuple containing the dictionary of resistance calculations and
                   the dictionary of k-factors used.
        """
        k_factors = {
            "Kd": self._o86.CL5_3_2_2(duration, pl, ps),
            "Kh": 1.0, # System factor
            "Kse": 1.0, # Service condition factor for Elasticity
            "Ksc": 1.0, # Service condition factor for Compression
            "Kt": 1.0, # Treatment factor
        }
        pr_calcs = {
            'width': self._o86.CL6_5_6_2_3(section, material, section.lu_width, **k_factors),
            'depth': self._o86.CL6_5_6_2_3(section, material, section.lu_depth, **k_factors),
        }
        return pr_calcs, k_factors

    def calculate(self) -> tuple[str, str]:
        """
        Performs the main stud wall design calculation and returns the results.

        This is the main orchestration method. It calls helper methods to calculate
        loads and combinations, then enters a nested loop to iterate through every
        possible design permutation (stud size, spacing, plys) for each level.
        It finds the most economical (optimal) valid design for each level.

        Returns:
            tuple[str, str]: A tuple containing the formatted summary output string
                             and the detailed output string.
        """
        self.final_results = {}
        summary_output = ""
        detailed_output = ""

        # Clear any existing results for this wall
        for wall_story in self.wall.stories:
            for result in wall_story.results:
                self.db_session.delete(result)
        self.db_session.commit()

        loads_df = self._calculate_loads()
        detailed_output += "\nUnfactored Total Loads per floor\n"
        detailed_output += loads_df.to_string() + "\n"

        combo_df = self._calculate_load_combinations(loads_df)
        detailed_output += "\nFactored Loads Combos per floor\n"
        detailed_output += combo_df.to_string() + "\n"

        # --- Main Design Loop ---
        # Iterate through each story of the wall.
        for level, wall_story in enumerate(self.wall.stories):
            h = wall_story.story.height
            load_dict = loads_df.loc[level + 1].to_dict()
            load_combo_dict = combo_df.loc[level + 1].to_dict()

            all_solutions_for_level = []
            db_results_for_level = []

            # Iterate through every available stud type.
            for stud_template in self._studs:
                # Iterate through every standard spacing.
                for spacing in self._spacings:
                    # Iterate through 1, 2, and 3 plys.
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

                        # Check the current design against every load combination.
                        for combo_name, load in load_combo_dict.items():
                            # Determine duration from load combination components for Kd factor.
                            has_live = 'L' in combo_name
                            has_snow = 'S' in combo_name

                            if not has_live and not has_snow:
                                duration = 'Long'
                                long, short = 0, 0
                            else:
                                duration = 'Standard'
                                # This is a simplification. A more robust implementation would
                                # analyze the combo items to determine the principal and companion loads.
                                long = load_dict['DL']
                                short = 0
                                if has_live:
                                    short += load_dict['LL']
                                if has_snow:
                                    short += load_dict['SL']

                            pf = load * (spacing / 1000) # Factored load per stud
                            pl = long * (spacing / 1000)
                            ps = short * (spacing / 1000)

                            pr_calcs, k_factors = self._size_stud(section, stud_template.material, duration, pl, ps)
                            # The resistance is the minimum of the resistance in the strong and weak axes.
                            pr = min(pr_calcs['width']['Pr'], pr_calcs['depth']['Pr']) / 1000
                            # Design Capacity (DC) ratio is Factored Load / Factored Resistance
                            dc = pf / pr if pr > 0 else float('inf')

                            # Keep track of the worst-case (governing) combination for this design.
                            if dc > max_dc_ratio:
                                max_dc_ratio = dc
                                governing_combo = combo_name
                                governing_result_for_design.Pf = pf
                                governing_result_for_design.Pr = pr
                                governing_result_for_design.k_factors = k_factors

                        governing_result_for_design.dc_ratio = max_dc_ratio
                        governing_result_for_design.governing_combo = governing_combo
                        governing_result_for_design.wood_volume = section.Ag / spacing
                        all_solutions_for_level.append(governing_result_for_design)

                        # Create and store the result in the database
                        if governing_result_for_design.dc_ratio < 1.0:
                            db_result = Result(
                                wall_story=wall_story,
                                stud_id=stud_template.id,
                                spacing=spacing,
                                plys=plys,
                                dc_ratio=max_dc_ratio,
                                governing_combo=governing_combo,
                                Pf=governing_result_for_design.Pf,
                                Pr=governing_result_for_design.Pr,
                                k_factors=k_factors,
                                wood_volume=governing_result_for_design.wood_volume,
                                is_final=False
                            )
                            db_results_for_level.append(db_result)
                            self.db_session.add(db_result)


            detailed_output += "\n---------------------------------------------------------\n"
            detailed_output += f"All Design Options for Level {level + 1}\n"

            all_solutions_for_level.sort(key=lambda x: (x.stud.section.depth, x.plys, x.spacing))

            # Format results for display
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

            # Filter for valid solutions (DC ratio < 1.0)
            valid_solutions = [s for s in all_solutions_for_level if s.dc_ratio < 1.0]

            if not valid_solutions:
                summary_output += f"Level {level + 1}: No adequate design found.\n"
                detailed_output += "\nNo adequate design found.\n"
                self.final_results[level] = DesignResult(level=level, story=wall_story.story, stud=None)
            else:
                # Find the optimal solution (lowest wood volume proxy)
                optimal_solution = sorted(valid_solutions, key=lambda x: x.wood_volume)[0]
                self.final_results[level] = optimal_solution

                # Mark the optimal solution as final in the database
                for db_result in db_results_for_level:
                    if (db_result.stud_id == optimal_solution.stud.id and
                            db_result.spacing == optimal_solution.spacing and
                            db_result.plys == optimal_solution.plys):
                        db_result.is_final = True
                        break

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

        self.db_session.commit()
        return summary_output, detailed_output

    def get_results(self):
        """Returns the dictionary of final results."""
        return self.final_results
