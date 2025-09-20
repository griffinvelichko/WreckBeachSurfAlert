"""
Unit tests for wind condition evaluation.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conditions import is_northwest, check_alert_condition


class TestConditions(unittest.TestCase):
    """Test wind condition evaluation functions."""

    def test_northwest_direction_center(self):
        """Test NW direction at center (315°)."""
        self.assertTrue(is_northwest(315))

    def test_northwest_direction_lower_bound(self):
        """Test NW direction at lower boundary (292.5°)."""
        self.assertTrue(is_northwest(292.5))

    def test_northwest_direction_upper_bound(self):
        """Test NW direction at upper boundary (337.5°)."""
        self.assertTrue(is_northwest(337.5))

    def test_not_northwest_south(self):
        """Test non-NW direction (South 180°)."""
        self.assertFalse(is_northwest(180))

    def test_not_northwest_east(self):
        """Test non-NW direction (East 90°)."""
        self.assertFalse(is_northwest(90))

    def test_not_northwest_just_outside_lower(self):
        """Test just outside NW lower bound (292°)."""
        self.assertFalse(is_northwest(292))

    def test_not_northwest_just_outside_upper(self):
        """Test just outside NW upper bound (338°)."""
        self.assertFalse(is_northwest(338))

    def test_alert_condition_met(self):
        """Test alert condition met (NW wind >= 25 km/h)."""
        self.assertTrue(check_alert_condition(25.0, 315))
        self.assertTrue(check_alert_condition(30.0, 320))

    def test_alert_condition_speed_too_low(self):
        """Test alert condition not met (speed < 25 km/h)."""
        self.assertFalse(check_alert_condition(24.9, 315))
        self.assertFalse(check_alert_condition(20.0, 320))

    def test_alert_condition_wrong_direction(self):
        """Test alert condition not met (not NW)."""
        self.assertFalse(check_alert_condition(30.0, 180))
        self.assertFalse(check_alert_condition(25.0, 90))

    def test_alert_condition_both_wrong(self):
        """Test alert condition not met (both criteria fail)."""
        self.assertFalse(check_alert_condition(20.0, 180))


if __name__ == '__main__':
    unittest.main()