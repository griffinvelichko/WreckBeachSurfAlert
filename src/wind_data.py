import requests
import xml.etree.ElementTree as ET
import logging
from typing import Dict, Optional
from .config import COORDINATES

log = logging.getLogger(__name__)

def parse_openmeteo(data: Dict) -> Dict:
    """Parse Open-Meteo API response."""
    try:
        # Get the first (current) hour data
        hourly = data.get('hourly', {})
        wind_speed = hourly.get('wind_speed_10m', [None])[0]
        wind_direction = hourly.get('wind_direction_10m', [None])[0]

        if wind_speed is None or wind_direction is None:
            raise ValueError("Missing wind data in response")

        return {
            'speed': float(wind_speed),
            'direction': float(wind_direction),
            'source': 'open-meteo'
        }
    except (KeyError, IndexError, ValueError) as e:
        log.error(f"Error parsing Open-Meteo data: {e}")
        raise

def fetch_eccc_data() -> Dict:
    """Fetch wind data from Environment Canada MSC Datamart (fallback)."""
    try:
        # Using YVR (Vancouver International Airport) as closest reliable station
        url = "https://dd.weather.gc.ca/observations/xml/BC/hourly/YVR_e.xml"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Parse XML
        root = ET.fromstring(response.text)

        # Find wind elements (using XPath)
        wind_speed_elem = root.find(".//windSpeed")
        wind_direction_elem = root.find(".//windDirection")

        if wind_speed_elem is None or wind_direction_elem is None:
            raise ValueError("Wind data not found in ECCC XML")

        # Extract values
        wind_speed = float(wind_speed_elem.text) if wind_speed_elem.text else 0

        # Wind direction might be in compass format (e.g., "NW") or degrees
        wind_dir_text = wind_direction_elem.text
        if wind_dir_text and wind_dir_text.isdigit():
            wind_direction = float(wind_dir_text)
        else:
            # Convert compass to degrees (simple mapping for NW winds)
            compass_to_degrees = {
                'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
                'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
                'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
                'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5
            }
            wind_direction = compass_to_degrees.get(wind_dir_text, 0)

        return {
            'speed': wind_speed,
            'direction': wind_direction,
            'source': 'eccc'
        }
    except Exception as e:
        log.error(f"Error fetching ECCC data: {e}")
        raise

def fetch_wind_data() -> Optional[Dict]:
    """Fetch wind data from Open-Meteo with ECCC fallback."""
    # Primary: Open-Meteo
    try:
        response = requests.get(
            'https://api.open-meteo.com/v1/forecast',
            params={
                'latitude': COORDINATES['lat'],
                'longitude': COORDINATES['lon'],
                'hourly': 'wind_speed_10m,wind_direction_10m',
                'wind_speed_unit': 'kmh',
                'forecast_hours': 1
            },
            timeout=10
        )
        if response.status_code == 200:
            return parse_openmeteo(response.json())
    except Exception as e:
        log.warning(f"Open-Meteo failed: {e}")

    # Fallback: ECCC
    try:
        log.info("Attempting ECCC fallback")
        return fetch_eccc_data()
    except Exception as e:
        log.error(f"All weather sources failed: {e}")
        return None