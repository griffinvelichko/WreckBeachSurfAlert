import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from .config import STATE_FILE_PATH, ALERT_COOLDOWN_HOURS, DAILY_ALERT_LIMIT

log = logging.getLogger(__name__)

def load_state() -> Dict:
    """Load alert state from file."""
    if os.path.exists(STATE_FILE_PATH):
        try:
            with open(STATE_FILE_PATH, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            log.warning(f"Error loading state file: {e}, using defaults")

    # Default state
    return {
        'last_alert_time': '2000-01-01T00:00:00',
        'last_alert_condition': '',
        'alert_count_today': 0,
        'last_reset_date': datetime.now().date().isoformat()
    }

def save_state(state: Dict) -> None:
    """Save alert state to file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(STATE_FILE_PATH), exist_ok=True)

        with open(STATE_FILE_PATH, 'w') as f:
            json.dump(state, f, indent=2)
        log.debug(f"State saved: {state}")
    except IOError as e:
        log.error(f"Error saving state: {e}")

def should_send_alert(current_state: Optional[Dict] = None) -> bool:
    """
    Check if we should send an alert based on deduplication rules.

    Rules:
    1. Cooldown: 6-hour minimum between alerts
    2. Daily limit: Maximum 4 alerts per day

    Returns:
        True if alert should be sent
    """
    if current_state is None:
        current_state = load_state()

    now = datetime.now()
    today = now.date().isoformat()

    # Reset daily counter if it's a new day
    if current_state.get('last_reset_date') != today:
        current_state['alert_count_today'] = 0
        current_state['last_reset_date'] = today
        save_state(current_state)

    # Check daily limit
    if current_state.get('alert_count_today', 0) >= DAILY_ALERT_LIMIT:
        log.info(f"Daily alert limit reached ({DAILY_ALERT_LIMIT})")
        return False

    # Check cooldown period
    try:
        last_alert = datetime.fromisoformat(current_state.get('last_alert_time', '2000-01-01'))
        hours_since = (now - last_alert).total_seconds() / 3600

        if hours_since < ALERT_COOLDOWN_HOURS:
            remaining = ALERT_COOLDOWN_HOURS - hours_since
            log.info(f"In cooldown period, {remaining:.1f} hours remaining")
            return False

    except (ValueError, TypeError) as e:
        log.warning(f"Error parsing last alert time: {e}")

    return True

def update_state(wind_speed: float, wind_direction: float, message: str = None) -> None:
    """Update state after sending an alert."""
    state = load_state()

    now = datetime.now()
    today = now.date().isoformat()

    # Reset counter if new day
    if state.get('last_reset_date') != today:
        state['alert_count_today'] = 0
        state['last_reset_date'] = today

    state['last_alert_time'] = now.isoformat()
    state['last_alert_condition'] = f"NW {wind_speed:.1f} km/h"
    state['alert_count_today'] = state.get('alert_count_today', 0) + 1

    if message:
        state['last_message'] = message

    save_state(state)
    log.info(f"State updated: alert #{state['alert_count_today']} today")