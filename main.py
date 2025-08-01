from src.core.units import Units
from src.core.calculator import StudWallCalculator
from src.models.wall import Wall

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
        "spacings": [16, 12, 8],  # in or mm
        "plys": [1,2,3],  # number of stud plys
        "roof_dead": 22,  # psf or kPa
        "roof_snow": 69,  # psf or kPa
        "floor_dead": 35,  # psf or kPa
        "floor_live": 40,  # psf or kPa
        "partitions": 20,  # psf or kPa
        "wall_sw": 12,  # ft or m
        "wall_roof_trib": 2,  # ft or m
        "wall_floor_trib": 11  # ft or m
    }

    calculator.set_inputs(**inputs)
    
    # Run calculations
    calculator.calculate()

if __name__ == "__main__":
    main()
