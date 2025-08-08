import csv
from pathlib import Path

import pandas as pd
from rich import print
from rich.pretty import pprint
from rich.progress import Progress

"""
This module defines the main StudWallCalculator class for performing
stud wall design calculations.
"""
import csv
from pathlib import Path

import pandas as pd
from rich import print
from rich.pretty import pprint
from rich.progress import Progress

from ..models.section import Section
from ..models.joist_and_plank import Joist_and_Plank
from ..models.O86 import O86_20
from ..core.units import Units, UnitSystem
from ..core.results import DesignResult


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
    O86 : O86_20
        An instance of the O86_20 class containing CSA O86-20 code calculations.
    jp_dict : dict
        A dictionary of wood material properties, keyed by species name.
    species_list : list
        A list of available wood species names.
    spacings : list
        A list of allowable stud spacings in millimeters.
    studs : list
        A list of pre-initialized Section objects for common lumber sizes.
    final_results : dict
        A dictionary storing the final DesignResult object for each floor level.
    """

    def __init__(self, units: Units = Units.Imperial):
        """
        Initializes the StudWallCalculator.

        This sets up the calculator with the specified unit system, loads all
        necessary data, and initializes default design parameters.

        Parameters
        ----------
        units : Units, optional
            The unit system to be used for inputs and outputs, by default
            Units.Imperial.
        """
        self.units = units
        self.unit_system = UnitSystem(units)

        # Initialize O86 code calculation helper
        self.O86 = O86_20

        # Load wood material properties from the database.
        self.load_materials()

        # Set allowable stud spacings (in millimeters).
        self.spacings = [406, 305, 203]  # Corresponds to 16", 12", 8"

        # Create a list of stud sections to be used in the design process.
        self.initialize_studs()

        # Initialize default inputs. These will be used if not overridden.
        self.set_inputs(
            wall_roof_trib=2,
            wall_floor_trib=11,
            wall_heights=[10, 10, 10, 10, 12],
            roof_dead=22,
            roof_snow=69,
            floor_dead=35,
            floor_live=40,
            partitions=20,
            wall_sw=12
        )

        # Initialize dictionary to store final results.
        self.final_results = {}

    def load_materials(self):
        """
        Load wood material properties from the CSV database.

        Reads the `joist_and_plank.csv` file from the data directory and
        creates Joist_and_Plank objects for each material specification.
        The loaded materials are stored in `self.jp_dict` keyed by species name.

        The CSV file must contain columns for all required wood properties
        as defined in the Joist_and_Plank class.
        """
        data_dir = Path(__file__).parent.parent / 'data'
        csv_path = data_dir / 'joist_and_plank.csv'

        self.jp_dict = {}
        self.species_list = []

        with open(csv_path, mode='r') as file:
            csvFile = csv.DictReader(file)
            for lines in csvFile:
                # Convert numeric strings to float, leave others as is.
                temp = {k: float(v) if v.replace('.', '', 1).isdigit() else v
                        for k, v in lines.items()}
                new_jp = Joist_and_Plank(**temp)
                self.species_list.append(new_jp.name)
                self.jp_dict[new_jp.name] = new_jp

    def initialize_studs(self):
        """
        Initializes a list of stud Section objects for common lumber sizes.

        This method creates Section objects for common dimensional lumber sizes
        (2x4, 2x6, 2x8). These sections are pre-configured with 'SPF No1/No2'
        grade lumber properties, which are loaded previously by `load_materials`.

        The generated list of stud sections is stored in `self.studs` and is
        used by the `calculate` method to iterate through design options.

        Note
        ----
        The material is currently hardcoded to 'SPF No1/No2'. Future versions
        could make this configurable to allow for different species and grades.
        """
        self.studs = [
            Section(38, 89, self.jp_dict['SPF No1/No2']),
            Section(38, 140, self.jp_dict['SPF No1/No2']),
            Section(38, 184, self.jp_dict['SPF No1/No2']),
        ]

    def set_inputs(self, **kwargs):
        """
        Set and convert all physical inputs to the internal metric system.

        This method takes all user-defined inputs as keyword arguments,
        converts them from the display unit system (e.g., Imperial) to the
        internal calculation system (Metric), and stores them as instance
        attributes.

        Parameters
        ----------
        **kwargs
            Arbitrary keyword arguments representing the design inputs.
            Supported parameters include:
            - `wall_roof_trib` (float): Roof tributary width (ft or m).
            - `wall_floor_trib` (float): Floor tributary width (ft or m).
            - `wall_heights` (list[float]): Wall heights per floor (ft or m).
            - `roof_dead` (float): Roof dead load (psf or kPa).
            - `roof_snow` (float): Roof snow load (psf or kPa).
            - `floor_dead` (float): Floor dead load (psf or kPa).
            - `floor_live` (float): Floor live load (psf or kPa).
            - `partitions` (float): Partition load (psf or kPa).
            - `wall_sw` (float): Wall self-weight (psf or kPa).
        """
        # All inputs are converted to and stored in metric units for consistency.
        self.wall_roof_trib_m = self.unit_system.to_metric(kwargs.get('wall_roof_trib', 2), 'length_ft_m')
        self.wall_floor_trib_m = self.unit_system.to_metric(kwargs.get('wall_floor_trib', 11), 'length_ft_m')
        self.wall_heights_mm = [self.unit_system.to_metric(h, 'length_ft_mm') for h in
                                kwargs.get('wall_heights', [10, 10, 10, 10, 12])]
        self.roof_dead_kpa = self.unit_system.to_metric(kwargs.get('roof_dead', 22), 'pressure')
        self.roof_snow_kpa = self.unit_system.to_metric(kwargs.get('roof_snow', 69), 'pressure')
        self.floor_dead_kpa = self.unit_system.to_metric(kwargs.get('floor_dead', 35), 'pressure')
        self.floor_live_kpa = self.unit_system.to_metric(kwargs.get('floor_live', 40), 'pressure')
        self.partitions_kpa = self.unit_system.to_metric(kwargs.get('partitions', 20), 'pressure')
        self.wall_sw_kpa = self.unit_system.to_metric(kwargs.get('wall_sw', 12), 'pressure')

        self.n_floors = len(self.wall_heights_mm)

    def calculate_loads(self):
        """
        Calculate and accumulate unfactored loads for all floors.

        Calculates the dead, live, and snow line loads (in kN/m) at each floor
        level based on the tributary areas and specified load values. It then
        accumulates these loads from the top floor down to the bottom floor.

        Returns
        -------
        pandas.DataFrame
            A DataFrame containing the cumulative unfactored Dead Load (DL),
            Live Load (LL), and Snow Load (SL) for each floor. The index
            represents the floor number (from top to bottom).
        """
        i = 0
        floors = {}
        # Calculate loads for each individual floor.
        while i < self.n_floors:
            if i == 0:  # Top floor (roof)
                # Line load (kN/m) = Area load (kPa) * Tributary width (m)
                dl = (self.roof_dead_kpa * self.wall_roof_trib_m +
                      self.wall_sw_kpa * (self.wall_heights_mm[i] / 1000))
                ll = 0
                sl = (self.roof_snow_kpa * self.wall_roof_trib_m)
            else:  # Typical floor
                dl = ((self.floor_dead_kpa + self.partitions_kpa) * self.wall_floor_trib_m +
                      self.wall_sw_kpa * (self.wall_heights_mm[i] / 1000))
                ll = (self.floor_live_kpa * self.wall_floor_trib_m)
                sl = 0

            floors[self.n_floors - i] = {'DL': dl, 'LL': ll, 'SL': sl}
            i += 1

        # Create a DataFrame and calculate the cumulative sum from top to bottom.
        floor_df = pd.DataFrame(floors).transpose()
        self.loads_df = floor_df.cumsum()
        return self.loads_df

    def calculate_combinations(self, loads_df):
        """
        Calculate factored load combinations according to building code.

        Applies the standard load factors from CSA O86-20 to the unfactored
        loads to generate the required factored load combinations.

        Parameters
        ----------
        loads_df : pandas.DataFrame
            DataFrame containing the unfactored cumulative loads per floor.

        Returns
        -------
        pandas.DataFrame
            A DataFrame containing the factored load for each combination. The
            index is the floor number, and columns are the combination names.
        """
        combo_dict = {}
        combo_dict['1.4DL'] = loads_df['DL'] * 1.4
        combo_dict['1.25DL+1.5LL+1.0SL'] = loads_df['DL'] * 1.25 + loads_df['LL'] * 1.5 + loads_df['SL'] * 1.0
        combo_dict['1.25DL+1.5SL+1.0LL'] = loads_df['DL'] * 1.25 + loads_df['SL'] * 1.5 + loads_df['LL'] * 1.0
        combo_dict['1.25DL+1.5LL'] = loads_df['DL'] * 1.25 + loads_df['LL'] * 1.5
        combo_dict['1.25DL+1.5SL'] = loads_df['DL'] * 1.25 + loads_df['SL'] * 1.5

        self.combo_df = pd.DataFrame(combo_dict)
        return self.combo_df

    def size_studs(self, stud, duration, Pl, Ps):
        """
        Calculates the factored axial compressive resistance (Pr) of a single stud.

        This method applies the relevant modification factors (k-factors) based
        on load duration and determines the compressive resistance of the stud
        section according to CSA O86-20 Clause 6.5.6. It calculates the
        resistance for buckling about both the strong and weak axes.

        Parameters
        ----------
        stud : Section
            The stud Section object to be analyzed.
        duration : str
            The load duration category ('Long', 'Standard', 'Short'). This is
            used to determine the Kd factor.
        Pl : float
            The long-term component of the factored axial load (in kN).
        Ps : float
            The short-term component of the factored axial load (in kN).

        Returns
        -------
        tuple[dict, dict]
            A tuple containing:
            - A dictionary with the factored resistance (Pr) and intermediate
              values for buckling about the 'width' and 'depth' axes.
            - A dictionary containing the modification factors (k_factors) used.
        """
        # Determine k-factors based on load duration and other conditions.
        k_factors = {
            "Kd": self.O86.CL5_3_2_2(duration, Pl, Ps),
            "Kh": 1.0,  # System factor for compression
            "Kse": 1.0,  # Service condition factor for sawn lumber
            "Ksc": 1.0,  # Service condition factor
            "Kt": 1.0,  # Treatment factor
        }

        # Determine axial capacity of the stud for buckling about each axis.
        pr_calcs = {
            'width': self.O86.CL6_5_6_2_3(stud, stud.lu['width'], **k_factors),
            'depth': self.O86.CL6_5_6_2_3(stud, stud.lu['depth'], **k_factors),
        }

        return pr_calcs, k_factors

    def calculate(self):
        """
        Performs the main stud wall design calculation and prints the results.

        This method orchestrates the entire design process. It first calculates
        the loads and load combinations, then iterates through each floor level
        to find the optimal stud design. The progress of the calculations and
        the results for each level are printed to the console as they are
        determined.

        The process for each level is as follows:
        1.  A progress bar is displayed for the current level's calculations.
        2.  The method exhaustively iterates through every stud, spacing, and ply
            combination.
        3.  For each combination, it checks against every load case. A design is
            only considered valid if its DC ratio is less than 1.0 for ALL load
            combinations.
        4.  Every valid design solution is stored in a list for that level.
        5.  After all combinations are checked, a list of all valid solutions is
            printed.
        6.  The solution with the lowest wood volume is selected from the list and
            printed as the final, optimal design for that level.

        The final optimal results are also stored in the `self.final_results`
        dictionary for programmatic access.
        """
        # Calculate and print unfactored loads and factored load combinations.
        self.loads_df = self.calculate_loads()
        print("\n[bold blue]Unfactored Total Loads per floor[/bold blue]")
        pprint(self.loads_df)

        self.combo_df = self.calculate_combinations(self.loads_df)
        print("\n[bold blue]Factored Loads Combos per floor[/bold blue]")
        pprint(self.combo_df)

        # Initialize a dictionary to store the final DesignResult for each level.
        self.final_results = {}

        # Iterate backwards through each floor level, from top to bottom.
        for level in range(self.n_floors, 0, -1):
            # Get the height and load data for the current level.
            h = self.wall_heights_mm[self.n_floors - level]
            load_dict = self.loads_df.loc[level].to_dict()
            load_combo_dict = self.combo_df.loc[level].to_dict()

            all_solutions_for_level = []
            num_combinations = len(self.studs) * len(self.spacings) * 3

            # Use a progress bar for the calculation of each level.
            with Progress() as progress:
                task = progress.add_task(f"[bold red]Processing Level {level}...[/bold red]", total=num_combinations)

                # Iterate through all design combinations.
                for stud_template in self.studs:
                    for spacing in self.spacings:
                        for plys in range(1, 4):
                            progress.update(task, advance=1)
                            stud = Section(stud_template.width, stud_template.depth, stud_template.material, plys)
                            stud.lu['width'] = 152
                            stud.lu['depth'] = h

                            governing_result_for_design = DesignResult(level=level, stud=stud, spacing=spacing, plys=plys)
                            
                            max_dc_ratio = 0
                            governing_combo = None
                            
                            for combo, load in load_combo_dict.items():
                                if combo == '1.4DL':
                                    duration, long, short = 'Long', 0, 0
                                elif combo == '1.25DL+1.5LL+1.0SL':
                                    duration = 'Standard'
                                    long = load_dict['DL']
                                    short = load_dict['LL'] + 0.5 * load_dict['SL']
                                elif combo == '1.25DL+1.5SL+1.0LL':
                                    duration = 'Standard'
                                    long = load_dict['DL']
                                    short = load_dict['SL'] + 0.5 * load_dict['LL']
                                elif combo == '1.25DL+1.5LL':
                                    duration = 'Standard'
                                    long = load_dict['DL']
                                    short = load_dict['LL']
                                elif combo == '1.25DL+1.5SL':
                                    duration = 'Standard'
                                    long = load_dict['DL']
                                    short = load_dict['SL']

                                Pf = load * spacing / 1000
                                Pl = long * spacing / 1000
                                Ps = short * spacing / 1000

                                pr_calcs, k_factors = self.size_studs(stud, duration, Pl, Ps)
                                Pr = min(pr_calcs['width']['Pr'], pr_calcs['depth']['Pr']) / 1000
                                DC = Pf / Pr if Pr > 0 else float('inf')

                                if DC > max_dc_ratio:
                                    max_dc_ratio = DC
                                    governing_combo = combo
                                    governing_result_for_design.Pf = Pf
                                    governing_result_for_design.Pr = Pr
                                    governing_result_for_design.k_factors = k_factors

                            governing_result_for_design.dc_ratio = max_dc_ratio
                            governing_result_for_design.governing_combo = governing_combo
                            governing_result_for_design.wood_volume = stud.area / spacing
                            all_solutions_for_level.append(governing_result_for_design)

            # --- Print results for the current level ---
            print("---------------------------------------------------------")
            print(f"[bold cyan]All Design Options for Level {level}[/bold cyan]")

            all_solutions_for_level.sort(key=lambda x: (x.stud.depth, x.plys, x.spacing))

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
            pprint(summary_df)

            valid_solutions = [s for s in all_solutions_for_level if s.dc_ratio < 1.0]

            if not valid_solutions:
                print("\n[bold yellow]No adequate design found.[/bold yellow]")
                self.final_results[level] = DesignResult(level=level, stud=None)
            else:
                # Select the optimal solution (lowest wood volume) and create a detailed DataFrame.
                optimal_solution = sorted(valid_solutions, key=lambda x: x.wood_volume)[0]
                self.final_results[level] = optimal_solution

                display_spacing = self.unit_system.from_metric(optimal_solution.spacing, 'length_in_mm')
                spacing_unit = self.unit_system.get_display_unit('length_in_mm')
                display_pf = self.unit_system.from_metric(optimal_solution.Pf, 'load')
                display_pr = self.unit_system.from_metric(optimal_solution.Pr, 'load')
                load_unit = self.unit_system.get_display_unit('load')

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

                print("\n---------------------------------------------------------")
                print(f"[bold red]Final (Optimal) Design for Level {level}[/bold red]")
                pprint(final_df)

            print("---------------------------------------------------------\n")
