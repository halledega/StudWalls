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
    _o86 : O86_20
        An instance of the O86_20 class containing CSA O86-20 code calculations.
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
        self._o86 = O86_20
        self.final_results = {}

        self._materials = self._load_materials()
        self._studs = self._initialize_studs()
        self._spacings = [406, 305, 203]  # Corresponds to 16", 12", 8"

        self._set_inputs(
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

    def _load_materials(self):
        """
        Load wood material properties from the CSV database.
        """
        data_dir = Path(__file__).parent.parent / 'data'
        csv_path = data_dir / 'joist_and_plank.csv'
        materials = {}
        with open(csv_path, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                temp = {k: float(v) if v.replace('.', '', 1).isdigit() else v for k, v in row.items()}
                material = Joist_and_Plank(**temp)
                materials[material.name] = material
        return materials

    def _initialize_studs(self):
        """
        Initializes a list of stud Section objects for common lumber sizes.
        """
        return [
            Section(38, 89, self._materials['SPF No1/No2']),
            Section(38, 140, self._materials['SPF No1/No2']),
            Section(38, 184, self._materials['SPF No1/No2']),
        ]

    def _set_inputs(self, **kwargs):
        """
        Set and convert all physical inputs to the internal metric system.
        """
        self.wall_roof_trib_m = self.unit_system.to_metric(kwargs.get('wall_roof_trib', 2), 'length_ft_m')
        self.wall_floor_trib_m = self.unit_system.to_metric(kwargs.get('wall_floor_trib', 11), 'length_ft_m')
        self.wall_heights_mm = [self.unit_system.to_metric(h, 'length_ft_mm') for h in kwargs.get('wall_heights', [10, 10, 10, 10, 12])]
        self.roof_dead_kpa = self.unit_system.to_metric(kwargs.get('roof_dead', 22), 'pressure')
        self.roof_snow_kpa = self.unit_system.to_metric(kwargs.get('roof_snow', 69), 'pressure')
        self.floor_dead_kpa = self.unit_system.to_metric(kwargs.get('floor_dead', 35), 'pressure')
        self.floor_live_kpa = self.unit_system.to_metric(kwargs.get('floor_live', 40), 'pressure')
        self.partitions_kpa = self.unit_system.to_metric(kwargs.get('partitions', 20), 'pressure')
        self.wall_sw_kpa = self.unit_system.to_metric(kwargs.get('wall_sw', 12), 'pressure')
        self.n_floors = len(self.wall_heights_mm)

    def _calculate_loads(self):
        """
        Calculate and accumulate unfactored loads for all floors.
        """
        floors = {}
        for i in range(self.n_floors):
            if i == 0:  # Top floor (roof)
                dl = (self.roof_dead_kpa * self.wall_roof_trib_m + self.wall_sw_kpa * (self.wall_heights_mm[i] / 1000))
                ll = 0
                sl = self.roof_snow_kpa * self.wall_roof_trib_m
            else:  # Typical floor
                dl = ((self.floor_dead_kpa + self.partitions_kpa) * self.wall_floor_trib_m + self.wall_sw_kpa * (self.wall_heights_mm[i] / 1000))
                ll = self.floor_live_kpa * self.wall_floor_trib_m
                sl = 0
        
            floors[self.n_floors - i] = {'DL': dl, 'LL': ll, 'SL': sl}
        
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

    def _size_stud(self, stud, duration, pl, ps):
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
            'width': self._o86.CL6_5_6_2_3(stud, stud.lu['width'], **k_factors),
            'depth': self._o86.CL6_5_6_2_3(stud, stud.lu['depth'], **k_factors),
        }
        return pr_calcs, k_factors

    def calculate(self):
        """
        Performs the main stud wall design calculation and prints the results.
        """
        loads_df = self._calculate_loads()
        print("\n[bold blue]Unfactored Total Loads per floor[/bold blue]")
        pprint(loads_df)

        combo_df = self._calculate_load_combinations(loads_df)
        print("\n[bold blue]Factored Loads Combos per floor[/bold blue]")
        pprint(combo_df)

        for level in range(self.n_floors, 0, -1):
            h = self.wall_heights_mm[self.n_floors - level]
            load_dict = loads_df.loc[level].to_dict()
            load_combo_dict = combo_df.loc[level].to_dict()

            all_solutions_for_level = []
            num_combinations = len(self._studs) * len(self._spacings) * 3

            with Progress() as progress:
                task = progress.add_task(f"[bold red]Processing Level {level}...[/bold red]", total=num_combinations)
                for stud_template in self._studs:
                    for spacing in self._spacings:
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
                                    duration, long, short = 'Standard', load_dict['DL'], load_dict['LL'] + 0.5 * load_dict['SL']
                                elif combo == '1.25DL+1.5SL+1.0LL':
                                    duration, long, short = 'Standard', load_dict['DL'], load_dict['SL'] + 0.5 * load_dict['LL']
                                elif combo == '1.25DL+1.5LL':
                                    duration, long, short = 'Standard', load_dict['DL'], load_dict['LL']
                                elif combo == '1.25DL+1.5SL':
                                    duration, long, short = 'Standard', load_dict['DL'], load_dict['SL']

                                pf = load * spacing / 1000
                                pl = long * spacing / 1000
                                ps = short * spacing / 1000

                                pr_calcs, k_factors = self._size_stud(stud, duration, pl, ps)
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
                            governing_result_for_design.wood_volume = stud.area / spacing
                            all_solutions_for_level.append(governing_result_for_design)

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
