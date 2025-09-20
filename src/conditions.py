import logging
from .config import WIND_SPEED_THRESHOLD_KMH

log = logging.getLogger(__name__)

def is_northwest(degrees: float) -> bool:
    """
    Check if wind direction is from northwest.
    NW sector: 292.5° to 337.5° (45° sector centered on 315°)
    """
    # Handle wrap-around at 360°
    return (degrees >= 292.5 and degrees <= 337.5) or \
           (degrees >= 292.5 - 360 and degrees <= 337.5 - 360)

def is_good_wind_direction(degrees: float) -> bool:
    """
    Check if wind direction is good for windsurfing/kitesurfing at Wreck Beach.
    Good directions: North (N), Northwest (NW), and West (W) with some flexibility.

    Using wider ranges for better coverage:
    - North: 337.5° to 22.5° (45° sector centered on 0°/360°)
    - Northwest: 292.5° to 337.5° (45° sector centered on 315°)
    - West: 247.5° to 292.5° (45° sector centered on 270°)

    This creates a continuous range from 247.5° to 22.5° (via 360°)
    """
    # Normalize to 0-360 range
    degrees = degrees % 360

    # Check if in the good range: W through NW to N
    # 247.5° to 22.5° (covering W, NW, N)
    return (degrees >= 247.5) or (degrees <= 22.5)

def check_alert_condition(wind_speed: float, wind_direction: float) -> bool:
    """
    Check if wind conditions meet alert criteria.

    Args:
        wind_speed: Wind speed in km/h
        wind_direction: Wind direction in degrees (0-360)

    Returns:
        True if conditions meet alert criteria (N/NW/W wind >= 25 km/h)
    """
    is_good_direction = is_good_wind_direction(wind_direction)
    is_strong = wind_speed >= WIND_SPEED_THRESHOLD_KMH

    log.debug(f"Wind check: speed={wind_speed:.1f} km/h, direction={wind_direction:.0f}°")
    log.debug(f"Good direction (N/NW/W): {is_good_direction}, Is strong: {is_strong}")

    return is_good_direction and is_strong