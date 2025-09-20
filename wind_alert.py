#!/usr/bin/env python3
"""
Wreck Beach Wind Alert System

Monitors wind conditions at Wreck Beach and sends SMS alerts
when north-westerly winds exceed 25 km/h.
"""

import argparse
import logging
import sys
from datetime import datetime
from typing import Dict, Optional

from src.logger import setup_logging
from src.wind_data import fetch_wind_data
from src.conditions import check_alert_condition
from src.state_manager import should_send_alert, update_state
from src.sms_sender import send_sms
from src.config import DRY_RUN

# Setup logging
log = setup_logging()

def create_alert_message(wind_speed: float, wind_direction: float) -> str:
    """
    Create a plain text alert message.

    Args:
        wind_speed: Wind speed in km/h
        wind_direction: Wind direction in degrees

    Returns:
        Alert message string
    """
    # Determine wind direction name
    def get_wind_direction_name(degrees: float) -> str:
        """Convert degrees to compass direction."""
        degrees = degrees % 360
        if degrees <= 11.25 or degrees >= 348.75:
            return "N"
        elif 11.25 < degrees <= 33.75:
            return "NNE"
        elif 33.75 < degrees <= 56.25:
            return "NE"
        elif 56.25 < degrees <= 78.75:
            return "ENE"
        elif 78.75 < degrees <= 101.25:
            return "E"
        elif 101.25 < degrees <= 123.75:
            return "ESE"
        elif 123.75 < degrees <= 146.25:
            return "SE"
        elif 146.25 < degrees <= 168.75:
            return "SSE"
        elif 168.75 < degrees <= 191.25:
            return "S"
        elif 191.25 < degrees <= 213.75:
            return "SSW"
        elif 213.75 < degrees <= 236.25:
            return "SW"
        elif 236.25 < degrees <= 258.75:
            return "WSW"
        elif 258.75 < degrees <= 281.25:
            return "W"
        elif 281.25 < degrees <= 303.75:
            return "WNW"
        elif 303.75 < degrees <= 326.25:
            return "NW"
        elif 326.25 < degrees <= 348.75:
            return "NNW"
        else:
            return "?"

    direction_name = get_wind_direction_name(wind_direction)

    # For now, simple message. OpenAI integration will be added in Phase G
    return f"🌊 {direction_name} wind {wind_speed:.0f} km/h at Wreck Beach! Perfect conditions for windsurfing."

def main(force_alert: bool = False,
         test_wind_speed: Optional[float] = None,
         test_wind_direction: Optional[float] = None) -> int:
    """
    Main execution function.

    Args:
        force_alert: Force sending an alert (for testing)
        test_wind_speed: Override wind speed for testing
        test_wind_direction: Override wind direction for testing

    Returns:
        Exit code (0 for success, 1 for error)
    """
    log.info("=== Starting Wreck Beach Wind Alert Check ===")
    log.info(f"Time: {datetime.now().isoformat()}")

    if DRY_RUN:
        log.info("Running in DRY RUN mode")

    try:
        # Fetch wind data (or use test data)
        if test_wind_speed is not None and test_wind_direction is not None:
            log.info(f"Using test wind data: {test_wind_speed} km/h @ {test_wind_direction}°")
            wind_data = {
                'speed': test_wind_speed,
                'direction': test_wind_direction,
                'source': 'test'
            }
        else:
            log.info("Fetching wind data...")
            wind_data = fetch_wind_data()

            if wind_data is None:
                log.error("Failed to fetch wind data from all sources")
                return 1

        wind_speed = wind_data['speed']
        wind_direction = wind_data['direction']
        source = wind_data['source']

        log.info(f"Wind data from {source}: {wind_speed:.1f} km/h @ {wind_direction:.0f}°")

        # Check alert conditions
        meets_criteria = check_alert_condition(wind_speed, wind_direction)

        if meets_criteria:
            log.info("✅ Wind conditions meet alert criteria")

            # Check deduplication
            if force_alert or should_send_alert():
                log.info("Sending alert...")

                # Create message
                message = create_alert_message(wind_speed, wind_direction)

                # Send SMS
                message_sid = send_sms(message)

                if message_sid:
                    log.info(f"Alert sent successfully! Message: {message}")

                    # Update state
                    if not DRY_RUN:
                        update_state(wind_speed, wind_direction, message)
                else:
                    log.error("Failed to send SMS")
                    return 1
            else:
                log.info("Alert suppressed due to deduplication rules")
        else:
            log.info("❌ Wind conditions do not meet alert criteria")

        log.info("=== Wind Alert Check Complete ===")
        return 0

    except Exception as e:
        log.error(f"Unexpected error: {e}", exc_info=True)
        return 1

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Wreck Beach Wind Alert System"
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without sending actual SMS alerts'
    )

    parser.add_argument(
        '--force-alert',
        action='store_true',
        help='Force sending an alert (bypass deduplication)'
    )

    parser.add_argument(
        '--test-wind-speed',
        type=float,
        help='Use test wind speed (km/h) instead of fetching real data'
    )

    parser.add_argument(
        '--test-wind-direction',
        type=float,
        help='Use test wind direction (degrees) instead of fetching real data'
    )

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()

    # Override DRY_RUN from command line if specified
    if args.dry_run:
        from src import config
        config.DRY_RUN = True

    # Both test parameters must be provided together
    if (args.test_wind_speed is not None) != (args.test_wind_direction is not None):
        log.error("Both --test-wind-speed and --test-wind-direction must be provided together")
        sys.exit(1)

    exit_code = main(
        force_alert=args.force_alert,
        test_wind_speed=args.test_wind_speed,
        test_wind_direction=args.test_wind_direction
    )

    sys.exit(exit_code)