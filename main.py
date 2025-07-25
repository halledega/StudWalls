from src.core.units import Units
from src.core.calculator import StudWallCalculator

def main():
    # --- CHOOSE YOUR UNIT SYSTEM HERE ---
    # units = Units.Metric
    units = Units.Imperial

    # Initialize calculator with the chosen unit system
    calculator = StudWallCalculator(units)
    
    # --- DEFINE YOUR INPUTS HERE (in the chosen unit system) ---
    # If using Imperial, inputs are in ft, psf, etc.
    # If using Metric, inputs are in m, kPa, etc.
    inputs = {
        "wall_heights": [10, 10, 10, 10, 12],  # ft or m
        "roof_dead": 22,  # psf or kPa
        "roof_snow": 69,  # psf or kPa
    }
    calculator.set_inputs(**inputs)
    
    # Run calculations
    calculator.calculate()
    
    # Print results
    calculator.print_results()

if __name__ == "__main__":
    main()
