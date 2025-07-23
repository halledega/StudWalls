import csv
import time
from pathlib import Path

import pandas as pd
from rich import print
from rich.pretty import pprint
from rich.progress import Progress

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from models import Section, Joist_and_Plank
from src.models.O86 import O86_20
from core.units import Units, get_conversion_factors

class StudWallCalculator:
    """A calculator for designing and analyzing wood stud walls according to CSA O86-20.
    
    This class handles the complete design process including:
    - Load calculation and accumulation through multiple floors
    - Load combination generation according to building code
    - Stud sizing and spacing optimization
    - Code compliance checks
    
    Attributes
    ----------
    units : Units
        The unit system to use (Imperial or Metric)
    factors : dict
        Conversion factors for different quantities based on unit system
    """
    
    def __init__(self, units: Units = Units.Imperial):
        """Initialize the calculator with specified units.
        
        Parameters
        ----------
        units : Units, optional
            The unit system to use, by default Units.Imperial
        """
        self.units = units
        self.factors = get_conversion_factors(units)
        
        # Initialize O86 code calculator
        self.O86 = O86_20
        
        # Load wood material properties
        self.load_materials()
        
        # Initialize default values
        self.wall_roof_trib = 2  # ft
        self.wall_floor_trib = 11  # ft
        self.wall_heights = [10, 10, 10, 10, 12]  # ft
        self.n_floors = len(self.wall_heights)
        
        # Set allowable spacings
        self.spacings = [406, 305, 203]  # mm
        
        # Create stud objects
        self.initialize_studs()
        
        # Define base loads
        self.roof_dead = 22  # psf
        self.roof_snow = 69  # psf
        self.floor_dead = 35  # psf
        self.floor_live = 40  # psf
        self.partitions = 20  # psf
        self.wall_sw = 12  # psf
        
    def load_materials(self):
        """Load wood material properties from the CSV database.
        
        Reads the joist_and_plank.csv file from the data directory and creates
        Joist_and_Plank objects for each material specification. Stores the
        materials in jp_dict keyed by species name.
        
        The CSV file should contain columns for all required wood properties
        as specified in the Joist_and_Plank class.
        """
        data_dir = Path(__file__).parent.parent / 'data'
        csv_path = data_dir / 'joist_and_plank.csv'
        
        self.jp_dict = {}
        self.species_list = []
        
        with open(csv_path, mode='r') as file:
            csvFile = csv.DictReader(file)
            for lines in csvFile:
                temp = {k: float(v) if v.replace('.','').isdigit() else v 
                       for k, v in lines.items()}
                new_jp = Joist_and_Plank(**temp)
                self.species_list.append(new_jp.name)
                self.jp_dict[new_jp.name] = new_jp

    def initialize_studs(self):
        """Initialize stud section objects for common lumber sizes.
        
        Creates Section objects for 2x4, 2x6, and 2x8 studs using SPF No1/No2
        grade lumber. Stores the sections in the studs list for use in
        design iterations.
        
        Note: Currently hardcoded for SPF No1/No2, could be made configurable
        for different species/grades in future versions.
        """
        self.s_2x4 = Section(38, 89, self.jp_dict['SPF No1/No2'])
        self.s_2x6 = Section(38, 140, self.jp_dict['SPF No1/No2'])
        self.s_2x8 = Section(38, 184, self.jp_dict['SPF No1/No2'])
        self.studs = [self.s_2x4, self.s_2x6, self.s_2x8]

    def configure_wall(self, **kwargs):
        """Configure wall parameters using keyword arguments.
        
        Parameters
        ----------
        **kwargs
            Arbitrary keyword arguments. Supported parameters include:
            - wall_roof_trib : float
                Roof tributary width in feet
            - wall_floor_trib : float
                Floor tributary width in feet
            - wall_heights : list of float
                Wall heights per floor in feet
            - roof_dead : float
                Roof dead load in psf
            - roof_snow : float
                Roof snow load in psf
            - floor_dead : float
                Floor dead load in psf
            - floor_live : float
                Floor live load in psf
            - partitions : float
                Partition load in psf
            - wall_sw : float
                Wall self-weight in psf
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.n_floors = len(self.wall_heights)

    def calculate_loads(self):
        """Calculate and accumulate loads for all floors.
        
        Calculates dead, live, and snow loads at each floor level based on
        tributary areas and load values. Accumulates loads from top to bottom
        of the wall. Handles both roof and floor conditions appropriately.
        
        Returns
        -------
        pandas.DataFrame
            DataFrame containing cumulative DL, LL, and SL for each floor.
            Index is floor number (top to bottom).
            Columns are 'DL', 'LL', 'SL' in kN/m.
        """
        i = 0
        floors = {}
        while i < self.n_floors:
            if i == 0:
                dl = (self.roof_dead * self.wall_roof_trib + self.wall_sw * self.wall_heights[i]) * self.factors['udl']
                ll = 0 * self.factors['udl']
                sl = (self.roof_snow * self.wall_roof_trib) * self.factors['udl']
            else:
                dl = ((self.floor_dead + self.partitions) * self.wall_floor_trib + 
                      self.wall_sw * self.wall_heights[i]) * self.factors['udl']
                ll = (self.floor_live * self.wall_floor_trib) * self.factors['udl']
                sl = 0 * self.factors['udl']
            
            floors[self.n_floors - i] = {
                'H': self.wall_heights[i],
                'DL': dl,
                'LL': ll,
                'SL': sl
            }
            i += 1
            
        floor_df = pd.DataFrame(floors).transpose()
        self.loads_df = floor_df.cumsum().drop(['H'], axis=1)
        return self.loads_df

    def calculate_combinations(self, loads_df):
        """Calculate load combinations according to building code requirements.
        
        Applies load factors and combines loads according to CSA O86-20:
        - 1.4DL
        - 1.25DL + 1.5LL + 1.0SL
        - 1.25DL + 1.5SL + 1.0LL
        - 1.25DL + 1.5LL
        - 1.25DL + 1.5SL
        
        Parameters
        ----------
        loads_df : pandas.DataFrame
            DataFrame containing unfactored loads per floor
            
        Returns
        -------
        pandas.DataFrame
            DataFrame containing factored load combinations.
            Index is floor number, columns are combination names.
        """
        combo_dict = {}
        combo_dict['1.4DL'] = loads_df['DL'] * 1.4
        combo_dict['1.25DL+1.5LL+1.0SL'] = loads_df['DL'] * 1.25 + loads_df['LL'] * 1.5 + loads_df['SL'] * 1.0
        combo_dict['1.25DL+1.5SL+1.0LL'] = loads_df['DL'] * 1.25 + loads_df['SL'] * 1.5 + loads_df['LL'] * 1.0
        combo_dict['1.25DL+1.5LL'] = loads_df['DL'] * 1.25 + loads_df['LL'] * 1.5
        combo_dict['1.25DL+1.5SL'] = loads_df['DL'] * 1.25 + loads_df['SL'] * 1.5
        
        self.combo_df = pd.DataFrame(combo_dict)
        return self.combo_df

    def size_studs(self, stud, spacing, combo, load, load_dict):
        """Calculate stud capacity and demand-capacity ratio for given configuration.
        
        Determines load duration factors, calculates axial capacity in both
        directions (width and depth), and computes demand-capacity ratios.
        
        Parameters
        ----------
        stud : Section
            The stud section to analyze
        spacing : float
            Stud spacing in mm
        combo : str
            Name of the load combination being checked
        load : float
            Factored load from the combination in kN/m
        load_dict : dict
            Dictionary containing unfactored DL, LL, SL values
            
        Returns
        -------
        dict
            Dictionary containing:
            - 'Pf': Factored axial load (kN)
            - 'Pr': Dictionary with axial capacities in both directions
            - 'DC': Governing demand-capacity ratio
            - 'k_factors': Dictionary of applicable k-factors
        """
        # Get long term and short term loads on stud
        if combo == '1.4DL':
            duration = 'Long'
            long = 0
            short = 0
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

        # Get factored axial load on stud
        Pf = load * spacing / 1000
        Pl = long * spacing / 1000
        Ps = short * spacing / 1000

        # Determine k factors
        k_factors = {
            "Kd": self.O86.CL5_3_2_2(duration, Pl, Ps),
            "Kh": 1.0,
            "Kse": 1.0,
            "Ksc": 1.0,
            "Kt": 1.0
        }

        # Determine axial capacity of stud in each direction
        Pr = {
            'Width': self.O86.CL6_5_6_2_3(stud, stud.Lu['Width'], **k_factors),
            'Depth': self.O86.CL6_5_6_2_3(stud, stud.Lu['Depth'], **k_factors)
        }

        # Determine the DC ratio in each direction
        DC = {
            'Width': Pf / (Pr['Width']['Pr'] / 1000),
            'Depth': Pf / (Pr['Depth']['Pr'] / 1000)
        }

        # Determine governing DC ratio
        DC = max(DC['Width'], DC['Depth'])

        return {
            'Pf': Pf,
            'Pr': Pr,
            'DC': DC,
            "k_factors": k_factors
        }

    def calculate(self):
        """Execute the complete stud wall design process.
        
        This method performs the following steps:
        1. Calculates loads for all floors
        2. Generates load combinations
        3. For each floor from top to bottom:
           - Starts with smallest stud size and maximum spacing
           - Checks all load combinations
           - If any DC > 1.0:
             a. Increases number of plys (up to 3)
             b. If still failing, reduces spacing
             c. If still failing, increases stud size
           - Stores results for all valid configurations
           - Identifies governing load combination
        
        The results are stored in instance variables:
        - loads_df: Unfactored loads
        - combo_df: Load combinations
        - results_dict: Results for each load combination
        - final_results_dict: Final design results
        - governing_lc: Governing load combination
        
        Raises
        ------
        RuntimeError
            If no valid solution can be found for a floor
        """
        # Calculate loads for all floors
        self.loads_df = self.calculate_loads()
        
        # Calculate load combinations
        self.combo_df = self.calculate_combinations(self.loads_df)
        
        # Set governing DC ratio
        DC_max = 1.0
        self.results = []
        self.results_dict = {}
        self.final_results_dict = {}
        
        with Progress() as progress:
            # Loop over floors (wall heights)
            for level in range(self.n_floors, 0, -1):
                task = progress.add_task(f"[bold red]Processing....{level}", total=100)
                
                # Set initial stud size to 2x4
                stud = self.studs[0]
                # Set initial stud spacing
                spacing = self.spacings[0]
                
                # Set height to height of current level
                h = self.wall_heights[self.n_floors - level] * self.factors['length']
                
                # Set unsupported lengths in each direction
                stud.Lu['Width'] = 0.152  # nail spacing
                stud.Lu['Depth'] = h  # wall height
                
                # Get dictionary of all load combos at current level
                load_dict = self.loads_df.loc[level].to_dict()
                load_combo_dict = self.combo_df.loc[level].to_dict()
                
                i = 0  # spacing iterator
                k = 0  # stud section iterator
                
                # Loop through all load combinations at current level
                for combo, load in load_combo_dict.items():
                    self.results_dict[combo] = self.size_studs(stud, spacing, combo, load, load_dict)
                    DC = self.results_dict[combo]['DC']
                    
                    while DC >= DC_max:
                        stud.Plys += 1  # increase plys
                        self.results_dict[combo] = self.size_studs(stud, spacing, combo, load, load_dict)
                        
                        if stud.Plys > 3:  # if max number of plys is reached (3)
                            stud.Plys = 1  # reset plys
                            i += 1
                            if i < len(self.spacings):
                                spacing = self.spacings[i]
                            
                        if i >= len(self.spacings):  # if min spacing is reached
                            i = 0  # reset spacing
                            k += 1  # increase stud size
                            if k < len(self.studs):
                                stud = self.studs[k]
                            
                        if k >= len(self.studs):  # nothing works
                            print("[bold red]No valid solution found![/bold red]")
                            break
                            
                        self.results_dict[combo] = self.size_studs(stud, spacing, combo, load, load_dict)
                        DC = self.results_dict[combo]['DC']
                    
                    self.results_dict[combo]['spacing'] = spacing
                    self.results_dict[combo]['stud'] = stud
                
                # Store final results for this level
                for combo, load in load_combo_dict.items():
                    self.final_results_dict[combo] = self.size_studs(stud, spacing, combo, load, load_dict)
                    self.final_results_dict[combo]['spacing'] = spacing
                    self.final_results_dict[combo]['stud'] = stud
                
                # Find governing load combination
                dc_list = []
                for combo in self.final_results_dict:
                    result = self.final_results_dict[combo]
                    dc_list.append(result['DC'])
                    governing_dc = max(dc_list)
                    if result['DC'] == governing_dc:
                        self.governing_lc = combo
                
                while not progress.finished:
                    progress.update(task, advance=20)
                    time.sleep(0.2)

    def print_results(self):
        """Print calculation results in a formatted manner.
        
        Displays:
        1. Summary of unfactored loads per floor
        2. Summary of load combinations per floor
        3. For each floor:
           - Results for each load combination
           - Stud configuration and DC ratios
           - Governing load combination and its results
        
        Uses rich library for formatted console output with colors
        and formatting for better readability.
        
        Note: This method should only be called after calculate()
        has been run successfully.
        """
        print("\n[bold blue]Unfactored Total Loads per floor[/bold blue]")
        pprint(self.loads_df)
        
        print("\n[bold blue]Factored Loads Combos per floor[/bold blue]")
        pprint(self.combo_df)
        
        for level in range(self.n_floors, 0, -1):
            print("---------------------------------------------------------")
            print(f"[bold red]Final Results for {level}[/bold red]")
            
            for combo in self.final_results_dict:
                result = self.final_results_dict[combo]
                print(f"[bold green]Results for {combo}[/bold green]")
                print(f"({result['stud'].Plys})-{result['stud'].Name} @ {result['spacing']} o/c")
                print(f"Pf = {result['Pf']}")
                print(f"Pr = {min(result['Pr']['Width']['Pr'], result['Pr']['Depth']['Pr']) / 1000}")
                print(f"DC = {result['DC']}")
            
            print("---------------------------------------------------------\n")
            print("[bold red]Results for Governing Load Combo[/bold red]")
            print(f"[bold green]Governing Combo: {self.governing_lc}[/bold green]")
            
            result = self.final_results_dict[self.governing_lc]
            print(f"({result['stud'].Plys})-{result['stud'].Name} {result['stud'].Material.name} @ {result['spacing']} o/c")
            print(f"Pf = {result['Pf']}")
            print(f"Pr = {min(result['Pr']['Width']['Pr'], result['Pr']['Depth']['Pr']) / 1000}")
            print(f"DC = {result['DC']}")
            print("---------------------------------------------------------\n")
