from src.core.units import Units
from src.core.calculator import StudWallCalculator

def main():
    # Initialize calculator with Imperial units
    calculator = StudWallCalculator(Units.Imperial)
    
    # Run calculations with default values
    calculator.calculate()
    
    # Print results
    calculator.print_results()

if __name__ == "__main__":
    main()
