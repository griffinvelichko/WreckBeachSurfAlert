"""
Unit tests for wind calculations.

As specified in Phase C Section 10: Testing Guidance
Test Cases:
1. Wind direction boundary tests (290°, 295°, 315°, 335°, 340°)
2. Unit conversion accuracy
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conditions import is_northwest, check_alert_condition
from src.unit_conversions import convert_wind_speed, CONVERSIONS


class TestWindCalculations(unittest.TestCase):
    """Test wind calculations and conversions."""

    # Test Case 1: Wind direction boundary tests
    def test_wind_direction_boundary_290(self):
        """Test boundary at 290° (just outside NW)."""
        self.assertFalse(is_northwest(290))

    def test_wind_direction_boundary_295(self):
        """Test boundary at 295° (inside NW)."""
        self.assertTrue(is_northwest(295))

    def test_wind_direction_boundary_315(self):
        """Test boundary at 315° (center of NW)."""
        self.assertTrue(is_northwest(315))

    def test_wind_direction_boundary_335(self):
        """Test boundary at 335° (inside NW)."""
        self.assertTrue(is_northwest(335))

    def test_wind_direction_boundary_340(self):
        """Test boundary at 340° (just outside NW)."""
        self.assertFalse(is_northwest(340))

    # Test Case 2: Unit conversion accuracy
    def test_kmh_to_ms_conversion(self):
        """Test km/h to m/s conversion."""
        # 25 km/h = 6.944 m/s (from plan)
        result = CONVERSIONS['kmh_to_ms'](25.0)
        self.assertAlmostEqual(result, 6.944, places=2)

    def test_ms_to_kmh_conversion(self):
        """Test m/s to km/h conversion."""
        # 1 m/s = 3.6 km/h
        result = CONVERSIONS['ms_to_kmh'](1.0)
        self.assertEqual(result, 3.6)

    def test_knots_to_kmh_conversion(self):
        """Test knots to km/h conversion."""
        # 13.499 knots = 25 km/h (approximately)
        result = CONVERSIONS['knots_to_kmh'](13.499)
        self.assertAlmostEqual(result, 25.0, places=1)

    def test_kmh_to_knots_conversion(self):
        """Test km/h to knots conversion."""
        # 25 km/h = 13.499 knots (from plan)
        result = CONVERSIONS['kmh_to_knots'](25.0)
        self.assertAlmostEqual(result, 13.499, places=2)

    def test_conversion_round_trip(self):
        """Test conversion round trip maintains value."""
        original = 25.0  # km/h

        # km/h -> m/s -> km/h
        ms_value = convert_wind_speed(original, 'kmh', 'ms')
        back_to_kmh = convert_wind_speed(ms_value, 'ms', 'kmh')
        self.assertAlmostEqual(original, back_to_kmh, places=1)

        # km/h -> knots -> km/h
        knots_value = convert_wind_speed(original, 'kmh', 'knots')
        back_to_kmh = convert_wind_speed(knots_value, 'knots', 'kmh')
        self.assertAlmostEqual(original, back_to_kmh, places=1)

    def test_alert_condition_with_exact_threshold(self):
        """Test alert condition at exact threshold (25 km/h)."""
        # Exactly at threshold should trigger
        self.assertTrue(check_alert_condition(25.0, 315))

    def test_alert_condition_just_below_threshold(self):
        """Test alert condition just below threshold (24.9 km/h)."""
        # Just below threshold should not trigger
        self.assertFalse(check_alert_condition(24.9, 315))

    def test_northwest_exact_boundaries(self):
        """Test exact NW boundaries (292.5° and 337.5°)."""
        # From plan: NW sector is 292.5° to 337.5°
        self.assertTrue(is_northwest(292.5))
        self.assertTrue(is_northwest(337.5))
        self.assertFalse(is_northwest(292.4))
        self.assertFalse(is_northwest(337.6))


if __name__ == '__main__':
    unittest.main()