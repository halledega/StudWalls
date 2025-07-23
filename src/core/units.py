from enum import Enum

class Units(Enum):
    Metric = 0
    Imperial = 1

def get_conversion_factors(units: Units):
    if units == Units.Imperial:
        return {
            'pressure': 1/20.885,  # psf to kPa
            'udl': 1/68.54,        # plf to kN/m
            'load': 4.448222/1000, # lb to kN
            'length': 1000/3.28    # ft to mm
        }
    else:
        return {
            'pressure': 1,
            'udl': 1,
            'load': 1,
            'length': 1
        }
