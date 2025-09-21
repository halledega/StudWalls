"""
This script serves as the main entry point for the StudWalls application.

It can be run in two modes:
1.  GUI Mode (default): Launches the PySide6 graphical user interface.
2.  CLI Mode: Runs a predefined design calculation directly in the console.
    (This is useful for testing the calculation engine).
"""

import sys
from PySide6 import QtWidgets as Qtw

# StudWall Imports
from src.core.units import Units
from src.core.calculator import StudWallCalculator
from src.ui.main_window.main_window import MainWindow

def run_calculator_cli():
    """
    Initializes and runs the stud wall design calculation in Command Line Interface (CLI) mode.

    This function is intended for development and testing purposes. It sets up a
    pre-defined wall configuration and runs the calculation, printing the results
    to the console without launching the GUI.
    """
    # --- CHOOSE YOUR UNIT SYSTEM HERE ---
    units = Units.Imperial

    # Initialize calculator with the chosen unit system
    calculator = StudWallCalculator(units)

    # --- DEFINE YOUR INPUTS HERE (in the chosen unit system) ---
    inputs = {
        "wall_heights": [9, 10, 10, 10, 10, 12],  # ft or m
        "roof_dead": 22,  # psf or kPa
        "roof_snow": 69,  # psf or kPa
        "floor_dead": 35,  # psf or kPa
        "floor_live": 40,  # psf or kPa
        "partitions": 20,  # psf or kPa
        "wall_sw": 12,  # psf or kPa (wall self-weight)
        "wall_roof_trib": 2,  # ft or m
        "wall_floor_trib": 11,  # ft or m
    }

    calculator._set_inputs(**inputs)

    # Run calculations
    calculator.calculate()


def main():
    """
    Initializes and runs the StudWalls Graphical User Interface (GUI).
    
    This is the primary entry point for the application.
    """
    # A QApplication instance is required for any PySide6 GUI application.
    # It manages application-wide resources and the event loop.
    app = Qtw.QApplication(sys.argv)
    
    # Create the main window object.
    window = MainWindow()
    
    # Start the application's event loop. The application will exit when the main window is closed.
    sys.exit(app.exec())


if __name__ == "__main__":
    # This standard Python construct ensures that the `main()` function is called
    # only when the script is executed directly (not when it's imported as a module).
    main()