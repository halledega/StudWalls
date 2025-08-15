"""
This script serves as the main entry point for running the stud wall calculator.

It demonstrates how to initialize the calculator, define input parameters,
and run the design calculations. Users can modify the inputs in this file
to analyze their specific wall configurations.
"""
# Import system
import sys
# Python Imports
# PySide6 Imports
from PySide6 import QtCore as Qtc
from PySide6 import QtWidgets as Qtw
from PySide6 import QtGui as Qtgui
# StudWall Imports
from src.core.units import Units
from src.core.calculator import StudWallCalculator
# UI Imports
from src.ui.main_window.main_window import Ui_MainWindow, MainWindow


def run_calculator_cli():
    """
    Initializes and runs the stud wall design calculation in CLI mode.

    This function sets the desired unit system, defines all necessary physical
    and loading parameters, passes them to the StudWallCalculator, and
n    initiates the calculation process.
    """
    # --- CHOOSE YOUR UNIT SYSTEM HERE ---
    # units = Units.Metric
    units = Units.Imperial

    # Initialize calculator with the chosen unit system
    calculator = StudWallCalculator(units)

    # --- DEFINE YOUR INPUTS HERE (in the chosen unit system) ---
    # If using Imperial, inputs are in ft, psf, etc.
    # If using Metric, inputs are in m, kPa, etc.
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
    Initializes and runs the stud wall calculator GUI.
    """
    # Create new QApplication instance
    app = Qtw.QApplication(sys.argv)
    # Create window object (could also be a widget)
    window = MainWindow()
    # Handle application shutdown
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

