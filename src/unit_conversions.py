"""
Unit conversion utilities for wind speed.

As specified in Phase C Section 6: Unit Normalization
"""

# Conversion functions as specified in the plan
CONVERSIONS = {
    'kmh_to_ms': lambda x: x / 3.6,
    'ms_to_kmh': lambda x: x * 3.6,
    'knots_to_kmh': lambda x: x * 1.852,
    'kmh_to_knots': lambda x: x / 1.852,
    'ms_to_knots': lambda x: x * 1.944,
    'knots_to_ms': lambda x: x / 1.944
}

def convert_wind_speed(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert wind speed between different units.

    Args:
        value: The wind speed value to convert
        from_unit: Source unit ('kmh', 'ms', 'knots')
        to_unit: Target unit ('kmh', 'ms', 'knots')

    Returns:
        Converted wind speed value
    """
    if from_unit == to_unit:
        return value

    # Convert to km/h first (normalize), then to target unit
    if from_unit == 'ms':
        kmh_value = CONVERSIONS['ms_to_kmh'](value)
    elif from_unit == 'knots':
        kmh_value = CONVERSIONS['knots_to_kmh'](value)
    else:
        kmh_value = value

    # Convert from km/h to target unit
    if to_unit == 'ms':
        return CONVERSIONS['kmh_to_ms'](kmh_value)
    elif to_unit == 'knots':
        return CONVERSIONS['kmh_to_knots'](kmh_value)
    else:
        return kmh_value

# Reference values from the plan:
# 1 m/s = 3.6 km/h = 1.944 knots
# 25 km/h = 6.944 m/s = 13.499 knots