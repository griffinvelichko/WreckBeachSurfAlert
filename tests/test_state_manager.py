"""
Unit tests for state management and deduplication.
"""

import unittest
import sys
import os
import json
import tempfile
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.state_manager import load_state, save_state, should_send_alert, update_state
from src import config


class TestStateManager(unittest.TestCase):
    """Test state management functions."""

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

    def test_load_state_default(self):
        """Test loading default state when file doesn't exist."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
        state = load_state()
        self.assertEqual(state['last_alert_time'], '2000-01-01T00:00:00')
        self.assertEqual(state['alert_count_today'], 0)

    def test_save_and_load_state(self):
        """Test saving and loading state."""
        test_state = {
            'last_alert_time': '2025-01-19T12:00:00',
            'last_alert_condition': 'NW 27 km/h',
            'alert_count_today': 2,
            'last_reset_date': '2025-01-19'
        }
        save_state(test_state)
        loaded = load_state()
        self.assertEqual(loaded['last_alert_time'], test_state['last_alert_time'])
        self.assertEqual(loaded['alert_count_today'], test_state['alert_count_today'])

    def test_should_send_alert_first_time(self):
        """Test should send alert on first run."""
        self.assertTrue(should_send_alert())

    def test_should_send_alert_cooldown(self):
        """Test cooldown period prevents alerts."""
        # Set last alert to 3 hours ago (within 6-hour cooldown)
        now = datetime.now()
        three_hours_ago = now - timedelta(hours=3)
        state = {
            'last_alert_time': three_hours_ago.isoformat(),
            'alert_count_today': 1,
            'last_reset_date': now.date().isoformat()
        }
        save_state(state)
        self.assertFalse(should_send_alert())

    def test_should_send_alert_after_cooldown(self):
        """Test alert allowed after cooldown expires."""
        # Set last alert to 7 hours ago (outside 6-hour cooldown)
        now = datetime.now()
        seven_hours_ago = now - timedelta(hours=7)
        state = {
            'last_alert_time': seven_hours_ago.isoformat(),
            'alert_count_today': 1,
            'last_reset_date': now.date().isoformat()
        }
        save_state(state)
        self.assertTrue(should_send_alert())

    def test_daily_limit(self):
        """Test daily limit prevents alerts."""
        now = datetime.now()
        seven_hours_ago = now - timedelta(hours=7)
        state = {
            'last_alert_time': seven_hours_ago.isoformat(),
            'alert_count_today': 4,  # At daily limit
            'last_reset_date': now.date().isoformat()
        }
        save_state(state)
        self.assertFalse(should_send_alert())

    def test_daily_reset(self):
        """Test daily counter resets on new day."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        state = {
            'last_alert_time': yesterday.isoformat(),
            'alert_count_today': 4,
            'last_reset_date': yesterday.date().isoformat()
        }
        save_state(state)
        self.assertTrue(should_send_alert())
        # Check counter was reset
        new_state = load_state()
        self.assertEqual(new_state['alert_count_today'], 0)

    def test_update_state(self):
        """Test state update after alert."""
        update_state(27.5, 315, "Test message")
        state = load_state()
        self.assertEqual(state['last_alert_condition'], 'NW 27.5 km/h')
        self.assertEqual(state['alert_count_today'], 1)
        self.assertEqual(state['last_message'], 'Test message')


if __name__ == '__main__':
    unittest.main()