# Wreck Beach Wind Alert System

Automated wind monitoring system for Wreck Beach, Vancouver, BC. Sends SMS alerts when north-westerly winds exceed 25 km/h.

## Features
- Monitors wind conditions every 60 minutes
- Sends SMS alerts via Twilio when conditions are met
- Uses OpenAI to generate entertaining surfer-style messages
- 6-hour cooldown between alerts to prevent spam
- Fallback weather data sources for reliability

## Setup

### Prerequisites
- Python 3.9+
- Twilio account with phone number
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Weather-Monitor
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

5. Configure your environment variables in `.env`

### Running Locally

For testing:
```bash
python wind_alert.py --dry-run
```

For production:
```bash
python wind_alert.py
```

## Deployment

The system is designed to run on GitHub Actions (free tier). See `.github/workflows/wind-alert.yml` for the schedule configuration.

## Architecture

- **Primary Weather API**: Open-Meteo (free, no authentication)
- **Fallback Weather API**: Environment Canada MSC Datamart
- **SMS Provider**: Twilio
- **Hosting**: GitHub Actions (cron schedule)
- **Message Generation**: OpenAI GPT API

## Wind Criteria

- **Direction**: North-westerly (292.5° to 337.5°)
- **Speed**: ≥ 25 km/h
- **Location**: Wreck Beach (49.2611°N, 123.2614°W)

## Cost Estimate

- Weather API: Free
- SMS: ~$0.01-0.02 per alert
- OpenAI: <$0.001 per alert
- Hosting: Free (GitHub Actions)
- **Total**: ~$0.40-2.00/month depending on alert frequency