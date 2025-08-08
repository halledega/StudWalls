import pytest
import pandas as pd
from src.core.calculator import StudWallCalculator
from src.core.units import Units

@pytest.fixture
def imperial_calculator():
    """Provides a StudWallCalculator instance configured for Imperial units and basic inputs."""
    calculator = StudWallCalculator(units=Units.Imperial)
    inputs = {
        "wall_heights": [10],
        "roof_dead": 20,
        "roof_snow": 40,
        "floor_dead": 0,
        "floor_live": 0,
        "partitions": 0,
        "wall_sw": 15,
        "wall_roof_trib": 10,
        "wall_floor_trib": 0,
    }
    calculator._set_inputs(**inputs)
    return calculator

def test_initialization():
    """Test that the calculator initializes correctly with both unit systems."""
    imperial_calc = StudWallCalculator(units=Units.Imperial)
    assert isinstance(imperial_calc, StudWallCalculator)
    assert imperial_calc.units == Units.Imperial

    metric_calc = StudWallCalculator(units=Units.Metric)
    assert isinstance(metric_calc, StudWallCalculator)
    assert metric_calc.units == Units.Metric

def test_input_conversion(imperial_calculator):
    """Test that imperial inputs are converted correctly to metric."""
    # 10 ft -> 3048 mm
    assert imperial_calculator.wall_heights_mm[0] == pytest.approx(3048)
    # 20 psf -> 0.9576 kPa
    assert imperial_calculator.roof_dead_kpa == pytest.approx(0.9576, abs=1e-4)
    # 40 psf -> 1.9152 kPa
    assert imperial_calculator.roof_snow_kpa == pytest.approx(1.9152, abs=1e-4)
    # 15 psf -> 0.7182 kPa
    assert imperial_calculator.wall_sw_kpa == pytest.approx(0.7182, abs=1e-4)
    # 10 ft -> 3.048 m
    assert imperial_calculator.wall_roof_trib_m == pytest.approx(3.048)

def test_load_calculation(imperial_calculator):
    """Test the unfactored load calculation for a single-story wall."""
    loads_df = imperial_calculator._calculate_loads()
    
    # Expected values based on the fixture's inputs
    expected_dl = (imperial_calculator.roof_dead_kpa * imperial_calculator.wall_roof_trib_m) + \
                  (imperial_calculator.wall_sw_kpa * (imperial_calculator.wall_heights_mm[0] / 1000))
    expected_sl = imperial_calculator.roof_snow_kpa * imperial_calculator.wall_roof_trib_m

    assert isinstance(loads_df, pd.DataFrame)
    assert loads_df.loc[1, 'DL'] == pytest.approx(expected_dl)
    assert loads_df.loc[1, 'SL'] == pytest.approx(expected_sl)
    assert loads_df.loc[1, 'LL'] == 0

def test_load_combinations(imperial_calculator):
    """Test the factored load combination calculations."""
    loads_df = imperial_calculator._calculate_loads()
    combo_df = imperial_calculator._calculate_load_combinations(loads_df)

    dl = loads_df.loc[1, 'DL']
    sl = loads_df.loc[1, 'SL']

    assert isinstance(combo_df, pd.DataFrame)
    assert combo_df.loc[1, '1.4DL'] == pytest.approx(1.4 * dl)
    assert combo_df.loc[1, '1.25DL+1.5SL'] == pytest.approx(1.25 * dl + 1.5 * sl)
    assert combo_df.loc[1, '1.25DL+1.5SL+1.0LL'] == pytest.approx(1.25 * dl + 1.5 * sl)

def test_end_to_end_calculation(imperial_calculator):
    """Test the full calculation process and verify the optimal result."""
    # Run the full calculation
    imperial_calculator.calculate()

    # The expected optimal result for the simple scenario in the fixture
    # is a 2x4 (38x89) stud at 16" (406mm) o/c.
    final_result = imperial_calculator.final_results[1]

    assert final_result.stud.name == "38x89"
    assert final_result.spacing == 406
    assert final_result.plys == 1
    # The DC ratio for this specific case should be ~0.56
    assert final_result.dc_ratio == pytest.approx(0.56, abs=1e-2)
