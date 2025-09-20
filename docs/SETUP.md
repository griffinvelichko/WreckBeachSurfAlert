# Setup Instructions

## Quick Setup

1. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
cp .env.example .env
```
Then edit `.env` with your actual credentials:
- Add your Twilio credentials (see docs/TWILIO_SETUP.md)
- Add your OpenAI API key (see docs/OPENAI_SETUP.md)
- Add your phone number for alerts

4. **Test the system:**
```bash
python wind_alert.py --dry-run --test-wind-speed 27 --test-wind-direction 315
```

## Verify Installation

Check that all modules are imported correctly:
```bash
python -c "import requests, twilio, dotenv, pytz, tenacity, openai; print('All dependencies installed!')"
```

## Next Steps

- See TEST_COMMANDS.md for testing examples
- Configure GitHub Actions for automated scheduling (Phase D)
- Add OpenAI integration for surfer messages (Phase G)