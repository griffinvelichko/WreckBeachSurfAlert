import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_FROM = os.getenv('TWILIO_PHONE_FROM')
ALERT_PHONE_TO = os.getenv('ALERT_PHONE_TO')

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Wreck Beach Coordinates (as specified in plan)
COORDINATES = {
    'lat': float(os.getenv('WRECK_BEACH_LAT', '49.2611')),
    'lon': float(os.getenv('WRECK_BEACH_LON', '-123.2614'))
}

# State Management
STATE_FILE_PATH = os.getenv('STATE_FILE_PATH', '/tmp/wind_alert_state.json')

# Alert Configuration
ALERT_COOLDOWN_HOURS = int(os.getenv('ALERT_COOLDOWN_HOURS', '6'))
WIND_SPEED_THRESHOLD_KMH = float(os.getenv('WIND_SPEED_THRESHOLD_KMH', '25.0'))
DAILY_ALERT_LIMIT = int(os.getenv('DAILY_ALERT_LIMIT', '4'))

# Application Settings
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')