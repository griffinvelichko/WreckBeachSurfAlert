"""
Unit tests for deduplication logic.

As specified in Phase C Section 10: Testing Guidance
Test Case 3: Deduplication with various time gaps
"""

import unittest
import sys
import os
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.state_manager import should_send_alert, update_state, load_state, save_state
from src import config


class TestDeduplication(unittest.TestCase):
    """Test deduplication logic with various time gaps."""

    def setUp(self):
        """Set up test with temporary state file."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.original_path = config.STATE_FILE_PATH
        config.STATE_FILE_PATH = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        """Clean up temporary file."""
        config.STATE_FILE_PATH = self.original_path
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_dedup_1_hour_gap(self):
        """Test deduplication with 1-hour gap (should block)."""
        # Set last alert to 1 hour ago
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        state = {
            'last_alert_time': one_hour_ago.isoformat(),
            'alert_count_today': 1,
            'last_reset_date': now.date().isoformat(),
            'last_alert_condition': 'NW 27 km/h'
        }
        save_state(state)

        # Should not send (within 6-hour cooldown)
        self.assertFalse(should_send_alert())

    def test_dedup_3_hour_gap(self):
        """Test deduplication with 3-hour gap (should block)."""
        # Set last alert to 3 hours ago
        now = datetime.now()
        three_hours_ago = now - timedelta(hours=3)
        state = {
            'last_alert_time': three_hours_ago.isoformat(),
            'alert_count_today': 1,
            'last_reset_date': now.date().isoformat(),
            'last_alert_condition': 'NW 27 km/h'
        }
        save_state(state)

        # Should not send (within 6-hour cooldown)
        self.assertFalse(should_send_alert())

    def test_dedup_5_hour_59_min_gap(self):
        """Test deduplication with 5:59 gap (should block)."""
        # Set last alert to 5 hours 59 minutes ago
        now = datetime.now()
        almost_six_hours_ago = now - timedelta(hours=5, minutes=59)
        state = {
            'last_alert_time': almost_six_hours_ago.isoformat(),
            'alert_count_today': 1,
            'last_reset_date': now.date().isoformat(),
            'last_alert_condition': 'NW 27 km/h'
        }
        save_state(state)

        # Should not send (still within 6-hour cooldown)
        self.assertFalse(should_send_alert())

    def test_dedup_6_hour_1_min_gap(self):
        """Test deduplication with 6:01 gap (should allow)."""
        # Set last alert to 6 hours 1 minute ago
        now = datetime.now()
        over_six_hours_ago = now - timedelta(hours=6, minutes=1)
        state = {
            'last_alert_time': over_six_hours_ago.isoformat(),
            'alert_count_today': 1,
            'last_reset_date': now.date().isoformat(),
            'last_alert_condition': 'NW 27 km/h'
        }
        save_state(state)

        # Should send (outside 6-hour cooldown)
        self.assertTrue(should_send_alert())

    def test_dedup_12_hour_gap(self):
        """Test deduplication with 12-hour gap (should allow)."""
        # Set last alert to 12 hours ago
        now = datetime.now()
        twelve_hours_ago = now - timedelta(hours=12)
        state = {
            'last_alert_time': twelve_hours_ago.isoformat(),
            'alert_count_today': 1,
            'last_reset_date': now.date().isoformat(),
            'last_alert_condition': 'NW 27 km/h'
        }
        save_state(state)

        # Should send (well outside 6-hour cooldown)
        self.assertTrue(should_send_alert())

    def test_dedup_24_hour_gap(self):
        """Test deduplication with 24-hour gap (should allow and reset counter)."""
        # Set last alert to 24 hours ago (yesterday)
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        state = {
            'last_alert_time': yesterday.isoformat(),
            'alert_count_today': 3,
            'last_reset_date': yesterday.date().isoformat(),
            'last_alert_condition': 'NW 27 km/h'
        }
        save_state(state)

        # Should send (new day, counter reset)
        self.assertTrue(should_send_alert())

        # Check that counter was reset
        new_state = load_state()
        self.assertEqual(new_state['alert_count_today'], 0)
        self.assertEqual(new_state['last_reset_date'], now.date().isoformat())

    def test_daily_limit_not_reached(self):
        """Test daily limit when not reached (3 alerts, limit is 4)."""
        now = datetime.now()
        seven_hours_ago = now - timedelta(hours=7)
        state = {
            'last_alert_time': seven_hours_ago.isoformat(),
            'alert_count_today': 3,
            'last_reset_date': now.date().isoformat(),
            'last_alert_condition': 'NW 27 km/h'
        }
        save_state(state)

        # Should send (outside cooldown, below daily limit)
        self.assertTrue(should_send_alert())

    def test_daily_limit_reached(self):
        """Test daily limit when reached (4 alerts)."""
        now = datetime.now()
        seven_hours_ago = now - timedelta(hours=7)
        state = {
            'last_alert_time': seven_hours_ago.isoformat(),
            'alert_count_today': 4,  # At limit
            'last_reset_date': now.date().isoformat(),
            'last_alert_condition': 'NW 27 km/h'
        }
        save_state(state)

        # Should not send (daily limit reached)
        self.assertFalse(should_send_alert())

    def test_state_update_increments_counter(self):
        """Test that updating state increments the daily counter."""
        # Start with no alerts today
        state = {
            'last_alert_time': '2000-01-01T00:00:00',
            'alert_count_today': 0,
            'last_reset_date': datetime.now().date().isoformat(),
            'last_alert_condition': ''
        }
        save_state(state)

        # Update state after an alert
        update_state(27.5, 315, "Test alert 1")
        new_state = load_state()
        self.assertEqual(new_state['alert_count_today'], 1)

        # Update again
        update_state(28.0, 320, "Test alert 2")
        new_state = load_state()
        self.assertEqual(new_state['alert_count_today'], 2)

    def test_cooldown_period_exact_6_hours(self):
        """Test cooldown at exactly 6 hours."""
        now = datetime.now()
        exactly_six_hours_ago = now - timedelta(hours=6)
        state = {
            'last_alert_time': exactly_six_hours_ago.isoformat(),
            'alert_count_today': 1,
            'last_reset_date': now.date().isoformat(),
            'last_alert_condition': 'NW 27 km/h'
        }
        save_state(state)

        # Exactly at 6 hours should allow (>= comparison)
        self.assertTrue(should_send_alert())


if __name__ == '__main__':
    unittest.main()