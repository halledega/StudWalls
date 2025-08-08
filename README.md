# StudWall Calculator

A simple yet powerful Python tool for the structural analysis and design of light-frame wood stud walls based on the **CSA O86-20** standard and loads from the **National Building Code of Canada (NBCC) 2020**.

This calculator automates the process of sizing studs for multi-story buildings by calculating cumulative axial loads and performing design checks for all valid lumber sizes, spacings, and ply combinations.

## Overview

The primary goal of this project is to provide engineers, designers, and students with a transparent and easy-to-use tool for stud wall design. The calculator takes basic architectural and loading information as input and iterates through a comprehensive set of design options to find the most economical solution for each floor level.

The core features include:
-   **Unit System Flexibility**: Supports both Metric and Imperial units for inputs and outputs.
-   **Cumulative Load Calculation**: Automatically calculates and accumulates dead, live, and snow loads from the roof down to the foundation.
-   **Comprehensive Design Checks**: Performs compressive resistance calculations according to CSA O86-20, including all relevant modification factors (k-factors).
-   **Optimal Solution Finding**: Identifies the most efficient design for each level based on a wood volume proxy.
-   **Clear & Detailed Output**: Presents all valid solutions and highlights the optimal choice for each floor, along with detailed calculation results.

## How to Use

To run the calculator, simply configure the inputs in the `main.py` script and execute it from your terminal.

### 1. Configure Inputs

Open `main.py` and modify the following sections:

**Choose the Unit System:**
Select either `Units.Metric` or `Units.Imperial`.

```python
# --- CHOOSE YOUR UNIT SYSTEM HERE ---
# units = Units.Metric
units = Units.Imperial
```

**Define Building and Load Parameters:**
Update the `inputs` dictionary with your project's specific values. Ensure the values correspond to the chosen unit system (e.g., feet and psf for Imperial, meters and kPa for Metric).

```python
# --- DEFINE YOUR INPUTS HERE ---
inputs = {
    "wall_heights": [10, 10, 10, 10, 12],  # ft or m
    "spacings": [16, 12, 8],              # in or mm
    "plys": [1, 2, 3],                   # number of stud plys
    "roof_dead": 22,                     # psf or kPa
    "roof_snow": 69,                     # psf or kPa
    "floor_dead": 35,                    # psf or kPa
    "floor_live": 40,                    # psf or kPa
    "partitions": 20,                    # psf or kPa
    "wall_sw": 12,                       # psf or kPa (wall self-weight)
    "wall_roof_trib": 2,                 # ft or m
    "wall_floor_trib": 11,               # ft or m
}
```

### 2. Run the Script

Execute the script from the root directory of the project:

```bash
python main.py
```

The script will print a detailed report for each floor level, showing all valid design solutions and highlighting the most economical one.

## Project Structure

The project is organized into the following directories and files:

```
.
├── main.py                     # Main entry point for running the calculator
├── src
│   ├── core
│   │   ├── calculator.py       # Core logic for the StudWallCalculator class
│   │   ├── results.py          # Defines the DesignResult data structure
│   │   └── units.py            # Handles unit conversions
│   │
│   ├── data
│   │   └── joist_and_plank.csv # Database of wood material properties
│   │
│   └── models
│       ├── O86.py              # Implements calculations from the CSA O86-20 standard
│       ├── section.py          # Defines the Section class for structural members
│       ├── wood.py             # Base class for wood materials
│       └── joist_and_plank.py  # Specialization of the Wood class
│
└── README.md                   # This file
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
