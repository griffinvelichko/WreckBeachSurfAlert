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

def check_alert_condition(wind_speed: float, wind_direction: float) -> bool:
    """
    Check if wind conditions meet alert criteria.

    Args:
        wind_speed: Wind speed in km/h
        wind_direction: Wind direction in degrees (0-360)

    Returns:
        True if conditions meet alert criteria (NW wind >= 25 km/h)
    """
    is_nw = is_northwest(wind_direction)
    is_strong = wind_speed >= WIND_SPEED_THRESHOLD_KMH

    log.debug(f"Wind check: speed={wind_speed:.1f} km/h, direction={wind_direction:.0f}°")
    log.debug(f"Is NW: {is_nw}, Is strong: {is_strong}")

    return is_nw and is_strong