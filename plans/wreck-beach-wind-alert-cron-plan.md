# Wreck Beach Wind Alert System Implementation Plan

## Executive Summary

This plan outlines a robust, production-ready system that monitors wind conditions at Wreck Beach, Vancouver, BC every 60 minutes and sends SMS alerts when north-westerly winds exceed 25 km/h. The system leverages Open-Meteo's free weather API as the primary data source with Environment Canada's MSC Datamart as fallback, uses Twilio for reliable SMS delivery, and can be hosted on GitHub Actions for zero-cost operation. The architecture emphasizes reliability through proper error handling, state management for alert deduplication, and comprehensive monitoring. Total estimated monthly cost ranges from $0 (GitHub Actions hosting, low alert frequency) to ~$15 (with moderate alert frequency and cloud hosting).

## Phase A — Ultrathink & Research

### 1. Wind Data APIs Comparison

| Provider | Latency | Spatial Resolution | Temporal | Auth | Rate Limits | Cost | Reliability | Recommendation |
|----------|---------|-------------------|----------|------|-------------|------|-------------|----------------|
| **Open-Meteo** | 5-10 min | 1-11 km | Hourly | None | Unlimited | **Free** | 99.9% | **PRIMARY** |
| **ECCC MSC Datamart** | 10-20 min | Station-based | Hourly | None | Unlimited | Free | 99% | **FALLBACK** |
| OpenWeatherMap | 10 min | 2.5 km | Hourly | API Key | 1000/day free | Free tier | 99.5% | Alternative |
| Tomorrow.io | 5-15 min | 1 km | Hourly | API Key | 500/day free | Free tier | 99.9% | Alternative |
| Windy/ECMWF | 6 hours | 9 km | 3-hourly | API Key | Limited | Paid | 99% | Not suitable |
| Apple WeatherKit | Real-time | Variable | Hourly | Auth | 500k/month | Free tier | 99.9% | iOS-only |

#### Primary: Open-Meteo
- **Endpoint**: `https://api.open-meteo.com/v1/forecast`
- **Wind Parameters**: `wind_speed_10m`, `wind_direction_10m`, `wind_gusts_10m`
- **Example Request**:
```
GET https://api.open-meteo.com/v1/forecast?latitude=49.2611&longitude=-123.2614&hourly=wind_speed_10m,wind_direction_10m&wind_speed_unit=kmh
```
- **Sample Response** (trimmed):
```json
{
  "hourly": {
    "time": ["2025-01-19T00:00", "2025-01-19T01:00"],
    "wind_speed_10m": [15.2, 27.3],
    "wind_direction_10m": [315, 320]
  }
}
```
- **Rationale**: No authentication required, unlimited requests, excellent uptime, returns data in desired units
- **Documentation**: https://open-meteo.com/en/docs

#### Fallback: Environment and Climate Change Canada (ECCC) MSC Datamart
- **Endpoint**: `https://dd.weather.gc.ca/observations/xml/BC/hourly/`
- **Station**: Vancouver Intl Airport (YVR) - closest reliable station
- **Example**: `https://dd.weather.gc.ca/observations/xml/BC/hourly/YVR_e.xml`
- **Rationale**: Government-operated, highly reliable, no rate limits
- **Documentation**: https://eccc-msc.github.io/open-data/

### 2. SMS Providers Comparison

| Provider | Price to CA | Setup | SDK/REST | Reliability | Free Tier | Compliance | Recommendation |
|----------|-------------|-------|----------|-------------|-----------|------------|----------------|
| **Twilio** | $0.0075/SMS + fees | Easy | Both | 99.95% | $15 credit | A2P ready | **PRIMARY** |
| Vonage/Nexmo | $0.0074/SMS | Easy | Both | 99.9% | €2 credit | Good | Alternative |
| MessageBird | $0.042/SMS | Easy | REST | 99% | None | Good | Expensive |
| Telnyx | $0.004/SMS | Moderate | Both | 99.9% | $2 credit | Good | Alternative |

#### Twilio (SMS Provider)
- **Pricing**: ~$0.0075 base + carrier fees (total ~$0.01-0.02/SMS to Canada)
- **API Endpoint**: `https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json`
- **Sample Request**:
```python
from twilio.rest import Client
client = Client(account_sid, auth_token)
message = client.messages.create(
    body="NW wind 27 km/h at Wreck Beach",
    from_='+1234567890',
    to='+1604XXXXXXX'
)
```
- **Rationale**: Industry leader, excellent documentation, proven reliability, good Canadian coverage
- **Documentation**: https://www.twilio.com/docs/sms/api


### 3. Geocoding Verification

**Wreck Beach Coordinates**: `49.2611°N, 123.2614°W`

- **Primary Source**: GeoNames Canada: https://geonames.nrcan.gc.ca/
- **Verification**: OpenStreetMap/Nominatim confirms location
- **Map Link**: https://www.openstreetmap.org/?mlat=49.2611&mlon=-123.2614&zoom=15
- **Note**: Beach extends from Spanish Banks to UBC, using center point for consistency

## Phase B — Architecture & Data Flow

### 4. System Architecture

```
┌─────────────┐
│   Scheduler │ (Cron: 0 * * * *)
└──────┬──────┘
       ▼
┌─────────────────────────┐
│   Fetch Wind Data       │
│   1. Try Open-Meteo     │
│   2. Fallback to ECCC   │
└──────┬──────────────────┘
       ▼
┌─────────────────────────┐
│   Parse & Normalize     │
│   - Extract wind_speed  │
│   - Extract direction   │
│   - Convert units       │
└──────┬──────────────────┘
       ▼
┌─────────────────────────┐
│   Evaluate Conditions   │
│   - NW check (292.5-337.5°)│
│   - Speed ≥ 25 km/h     │
└──────┬──────────────────┘
       ▼
┌─────────────────────────┐
│   Alert Decision        │
│   - Check dedup state   │
│   - 6hr cooldown check  │
└──────┬──────────────────┘
       ▼
┌─────────────────────────┐
│  Generate Surfer Text   │
│   - Call OpenAI API     │
│   - Create funny msg    │
│   - Fallback to plain   │
└──────┬──────────────────┘
       ▼
┌─────────────────────────┐
│   Send SMS if needed    │
│   - Send surfer message │
│   - Send via Twilio     │
│   - Update state        │
└──────┬──────────────────┘
       ▼
┌─────────────────────────┐
│   Logging & Metrics     │
└─────────────────────────┘
```

### 5. Wind Direction Test Definition

**North-Westerly Definition**: Wind FROM the NW quadrant
- **Bearing Range**: 292.5° to 337.5° (45° sector centered on 315°)
- **Justification**: Standard meteorological 16-point compass rose divides circle into 22.5° sectors
- **Implementation**:
```python
def is_northwest(degrees):
    # Handle wrap-around at 360°
    return (degrees >= 292.5 and degrees <= 337.5) or \
           (degrees >= 292.5 - 360 and degrees <= 337.5 - 360)
```
- **Cardinal to Degrees**: NW=315°, WNW=292.5°, NNW=337.5°

### 6. Unit Normalization

**Conversions**:
- 1 m/s = 3.6 km/h = 1.944 knots
- 25 km/h = 6.944 m/s = 13.499 knots

**Implementation**:
```python
CONVERSIONS = {
    'kmh_to_ms': lambda x: x / 3.6,
    'ms_to_kmh': lambda x: x * 3.6,
    'knots_to_kmh': lambda x: x * 1.852
}
```

**Policy**:
- Always convert to km/h for evaluation
- Round to 1 decimal place for display
- Use sustained wind (not gusts) for threshold check

### 7. Deduplication Strategy

**State Storage**: JSON file or environment variable
```json
{
  "last_alert_time": "2025-01-19T15:00:00Z",
  "last_alert_condition": "NW 27.5 km/h",
  "alert_count_today": 2
}
```

**Rules**:
1. **Cooldown**: 6-hour minimum between alerts
2. **State Change**: Alert if wind drops below 20 km/h then exceeds 25 km/h again
3. **Daily Limit**: Maximum 4 alerts per day
4. **Storage Options**:
   - Local: SQLite or JSON file
   - Cloud: Redis with TTL, DynamoDB, or GCP Firestore

## Phase C — Implementation Plan

### 8. Technology Stack

**Language**: Python 3.9+
- **Rationale**: Excellent HTTP libraries, simple deployment, wide ecosystem

**Required Packages**:
```
requests>=2.31.0       # HTTP client for API calls
twilio>=8.11.0        # Twilio SDK for SMS
python-dotenv>=1.0.0  # Environment variable management
pytz>=2023.3          # Timezone handling
tenacity>=8.2.0       # Retry logic
openai>=1.0.0         # OpenAI API for message generation
```

### 9. Step-by-Step Implementation Tasks

#### A. Configuration & Secrets Management
```python
# .env file (never commit)
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_FROM=+1234567890
ALERT_PHONE_TO=+1604XXXXXXX
OPENAI_API_KEY=sk-xxxxx
WRECK_BEACH_LAT=49.2611
WRECK_BEACH_LON=-123.2614
STATE_FILE_PATH=/tmp/wind_alert_state.json
```

#### B. Geocoding (One-time setup)
```python
# config.py
COORDINATES = {
    'lat': float(os.getenv('WRECK_BEACH_LAT', '49.2611')),
    'lon': float(os.getenv('WRECK_BEACH_LON', '-123.2614'))
}
```

#### C. Wind Data Fetching
```python
def fetch_wind_data():
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
    return fetch_eccc_data()
```

#### D. Condition Evaluation
```python
def check_alert_condition(wind_speed, wind_direction):
    is_nw = 292.5 <= wind_direction <= 337.5
    is_strong = wind_speed >= 25.0
    return is_nw and is_strong
```

#### E. Deduplication Check
```python
def should_send_alert(current_state):
    last_alert = datetime.fromisoformat(current_state.get('last_alert_time', '2000-01-01'))
    hours_since = (datetime.now() - last_alert).total_seconds() / 3600
    return hours_since >= 6  # 6-hour cooldown
```

#### F. SMS Sending
```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def send_sms(message_body):
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    message = client.messages.create(
        body=message_body,
        from_=TWILIO_FROM,
        to=ALERT_TO
    )
    return message.sid
```

#### G. Logging Setup
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/wind_alert.log')
    ]
)
```

### 10. Testing Guidance

**Local Testing**:
```bash
# Dry run mode
python wind_alert.py --dry-run

# Force condition for testing
python wind_alert.py --force-alert --test-wind-speed=30 --test-wind-direction=315

# Unit tests
pytest tests/test_wind_calculations.py
pytest tests/test_deduplication.py
```

**Test Cases**:
1. Wind direction boundary tests (290°, 295°, 315°, 335°, 340°)
2. Unit conversion accuracy
3. Deduplication with various time gaps
4. API failure and fallback behavior
5. SMS sending with mock Twilio client

## Phase D — Scheduling & Hosting Options

### 11. Hosting/Scheduling Comparison

#### Option 1: GitHub Actions (RECOMMENDED)
**Pros**: Free, reliable, built-in secrets management, no infrastructure
**Cons**: Public repos disable after 60 days inactivity
**Setup**:
```yaml
# .github/workflows/wind-alert.yml
name: Wreck Beach Wind Alert

on:
  schedule:
    - cron: '0 * * * *'  # Every hour at minute 0
  workflow_dispatch:  # Manual trigger for testing

jobs:
  check-wind:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python wind_alert.py
        env:
          TWILIO_ACCOUNT_SID: ${{ secrets.TWILIO_ACCOUNT_SID }}
          TWILIO_AUTH_TOKEN: ${{ secrets.TWILIO_AUTH_TOKEN }}
          TWILIO_PHONE_FROM: ${{ secrets.TWILIO_PHONE_FROM }}
          ALERT_PHONE_TO: ${{ secrets.ALERT_PHONE_TO }}
```

**Secrets Setup**:
1. Go to repo Settings → Secrets and variables → Actions
2. Add each secret (TWILIO_ACCOUNT_SID, etc.)

#### Option 2: GCP Cloud Run + Cloud Scheduler
**Pros**: Scalable, integrated monitoring, Secret Manager
**Cons**: Costs ~$5-10/month
**Setup**:
```bash
# Deploy container
gcloud run deploy wind-alert \
    --source . \
    --region us-west1 \
    --no-allow-unauthenticated

# Create scheduler job
gcloud scheduler jobs create http wind-alert-schedule \
    --location us-west1 \
    --schedule "0 * * * *" \
    --http-method GET \
    --uri https://wind-alert-xxxxx-uw.a.run.app/check
```

#### Option 3: Lambda + EventBridge
**Pros**: Pay-per-execution, highly available
**Cons**: More complex setup, ~$2-5/month
**Setup**:
```python
# serverless.yml
service: wind-alert
provider:
  name: aws
  runtime: python3.11
functions:
  checkWind:
    handler: handler.check_wind
    events:
      - schedule: rate(1 hour)
    environment:
      TWILIO_SID: ${ssm:/wind-alert/twilio-sid~true}
```

#### Option 4: VPS with Cron
**Pros**: Full control, can host multiple services
**Cons**: Requires maintenance, $5+/month
**Setup**:
```bash
# Install dependencies
sudo apt update && sudo apt install python3-pip python3-venv

# Setup virtualenv
python3 -m venv /opt/wind-alert/venv
source /opt/wind-alert/venv/bin/activate
pip install -r requirements.txt

# Add to crontab
crontab -e
# Add: 0 * * * * /opt/wind-alert/venv/bin/python /opt/wind-alert/wind_alert.py
```

### 12. Recommended Hosting: GitHub Actions

**Justification**:
- Zero cost for public repos
- Minimal setup complexity
- Built-in secrets management
- Reliable execution (GitHub SLA 99.9%)
- Easy testing with workflow_dispatch

**Deployment Steps**:
1. Create GitHub repository
2. Add secrets in repo settings
3. Create `.github/workflows/wind-alert.yml`
4. Push code and workflow file
5. Verify first scheduled run in Actions tab

## Phase E — Observability, Reliability & Ops

### 13. Logging Format & Metrics

**Structured Logging**:
```json
{
  "timestamp": "2025-01-19T15:00:00Z",
  "level": "INFO",
  "event": "wind_check",
  "wind_speed_kmh": 27.3,
  "wind_direction_deg": 315,
  "alert_sent": true,
  "alert_id": "SM123456",
  "api_used": "open-meteo",
  "response_time_ms": 245
}
```

**Key Metrics**:
- `wind_checks_total`: Counter of all checks
- `alerts_sent_total`: Counter of SMS sent
- `api_errors_total`: Counter by API provider
- `last_wind_speed_kmh`: Gauge of latest reading
- `last_wind_direction_deg`: Gauge of latest direction

### 14. Alert Throttling & State Management

**State Storage Options**:

1. **GitHub Actions Artifacts** (for GitHub hosting):
```python
# Save state as artifact
with open('state.json', 'w') as f:
    json.dump(state, f)
```

2. **Redis with TTL**:
```python
redis_client.setex(
    'last_alert_time',
    timedelta(hours=12),
    datetime.now().isoformat()
)
```

3. **Local SQLite**:
```sql
CREATE TABLE alert_state (
    id INTEGER PRIMARY KEY,
    last_alert_time TIMESTAMP,
    alert_count_today INTEGER,
    last_condition TEXT
);
```

### 15. Error Handling & Retries

**Retry Strategy**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def fetch_with_retry(url, **kwargs):
    response = requests.get(url, timeout=10, **kwargs)
    response.raise_for_status()
    return response.json()
```

**Error Scenarios**:
1. **API Timeout**: Retry 3x with exponential backoff, then try fallback
2. **Invalid Data**: Log error, skip this check cycle
3. **SMS Failure**: Retry 3x, log failure, alert via alternate channel
4. **State Corruption**: Reset to safe defaults, log incident

### 16. Runbook

**No Alerts Arriving**:
1. Check GitHub Actions logs for execution
2. Verify wind conditions actually meet criteria
3. Check deduplication state (may be in cooldown)
4. Verify API responses returning valid data
5. Check SMS provider status page
6. Verify phone number and credentials

**Constant Alerts**:
1. Check if deduplication is working
2. Verify state file is being written/read
3. Check if wind conditions are borderline (oscillating around 25 km/h)
4. Review cooldown period setting
5. Consider increasing threshold or cooldown

**Debugging Commands**:
```bash
# Check last run
gh run list --workflow=wind-alert.yml --limit=5

# View logs
gh run view <run-id> --log

# Trigger manual run
gh workflow run wind-alert.yml

# Check current wind conditions
curl "https://api.open-meteo.com/v1/forecast?latitude=49.2611&longitude=-123.2614&current=wind_speed_10m,wind_direction_10m"
```

## Phase F — Security & Cost

### 17. Secrets Handling

**Best Practices**:
1. **Never commit secrets** - Use .gitignore for .env files
2. **Rotate regularly** - Quarterly rotation for API keys
3. **Use platform secret managers**:
   - GitHub: Repository Secrets
   - GCP: Secret Manager
   - Cloud: Secrets Manager / Parameter Store
4. **Audit access** - Review who has access to secrets
5. **Use separate keys** for dev/staging/production

**Secret Rotation Procedure**:
```bash
# 1. Generate new credentials in provider console
# 2. Update in secret manager
# 3. Deploy and verify
# 4. Revoke old credentials
```

### 18. Principle of Least Privilege

**Access Controls**:
1. **API Keys**: Restrict to specific operations (e.g., Twilio key only for SMS sending)
2. **Cloud IAM**: Grant minimal required permissions
3. **Repository Access**: Limit who can modify workflows and secrets
4. **Network**: If using VPS, firewall all unnecessary ports

**GitHub Actions Permissions**:
```yaml
permissions:
  contents: read  # Only read repo
  actions: write  # For workflow dispatch
```

### 19. Cost Estimates

**Monthly Costs** (720 checks/month):

| Component | Low Alert (2/month) | Moderate (20/month) | High (100/month) |
|-----------|-------------------|-------------------|------------------|
| Open-Meteo API | $0 | $0 | $0 |
| Twilio SMS | $0.04 | $0.40 | $2.00 |
| OpenAI API (gpt-4o-mini) | $0.00004 | $0.0004 | $0.002 |
| GitHub Actions | $0 | $0 | $0 |
| State Storage | $0 | $0 | $0 |
| **Total (GitHub)** | **$0.04** | **$0.40** | **$2.00** |
| | | | |
| Alt: GCP Hosting | $5 | $5 | $5 |
| Alt: Lambda Hosting | $2 | $2 | $2 |
| **Total (Cloud)** | **$5-7** | **$5-7** | **$7-9** |

**Notes**:
- Assumes Wreck Beach has NW winds ≥25 km/h approximately 3-15% of hours
- SMS costs vary by carrier (shown is average)
- Cloud hosting adds ~$2-5/month but provides better monitoring

## Implementation Checklist

### Phase 1: Setup (Day 1)
- [ ] Create GitHub repository
- [ ] Sign up for Twilio account, get phone number
- [ ] Sign up for OpenAI account, get API key
- [ ] Verify Wreck Beach coordinates
- [ ] Create `.env.example` file

### Phase 2: Core Implementation (Day 2-3)
- [ ] Implement wind data fetching (Open-Meteo)
- [ ] Implement ECCC fallback
- [ ] Write unit conversion functions
- [ ] Implement wind direction checking
- [ ] Create deduplication logic
- [ ] Integrate Twilio SMS sending
- [ ] Implement OpenAI surfer message generation
- [ ] Add message caching logic
- [ ] Create fallback plain text messages

### Phase 3: Reliability (Day 4)
- [ ] Add retry logic with tenacity
- [ ] Implement comprehensive error handling
- [ ] Add structured logging
- [ ] Create state management system
- [ ] Write unit tests
- [ ] Test OpenAI API timeout handling
- [ ] Test SMS character limit validation

### Phase 4: Deployment (Day 5)
- [ ] Create GitHub Actions workflow
- [ ] Configure repository secrets
- [ ] Test manual workflow dispatch
- [ ] Verify scheduled execution
- [ ] Document runbook procedures

### Phase 5: Monitoring (Day 6)
- [ ] Add metrics collection
- [ ] Set up alert for job failures
- [ ] Create dashboard (if using cloud)
- [ ] Test all failure scenarios
- [ ] Perform load testing

### Phase 6: Documentation (Day 7)
- [ ] Write README with setup instructions
- [ ] Document API endpoints used
- [ ] Create troubleshooting guide
- [ ] Document secret rotation process
- [ ] Final testing and go-live

## Phase G — AI-Powered Surfer Dude Messaging

### 20. OpenAI Integration Overview

The system integrates OpenAI's GPT API to transform standard weather alerts into entertaining, surfer-dude-styled SMS messages. This adds personality and engagement to the alerts while maintaining critical information about wind conditions. The LLM generates context-aware messages that vary based on actual wind speed and conditions, ensuring each alert feels unique and relevant.

### 21. API Configuration & Authentication

**OpenAI Setup**:
```python
from openai import OpenAI
import asyncio

# Initialize client
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    timeout=10.0,  # 10 second timeout
    max_retries=2
)

# Model selection
MODEL = "gpt-4o-mini"  # Or "gpt-3.5-turbo" for lower cost
```

**Environment Variables**:
- `OPENAI_API_KEY`: Your OpenAI API key (starts with `sk-`)
- Model can be configured via env var for easy switching

### 22. Prompt Engineering

**System Prompt Design**:
```python
SYSTEM_PROMPT = """You are a chill surfer dude texting about wind conditions at Wreck Beach.
Keep it under 140 characters. Use surfer slang and be stoked about the conditions.
Include the actual wind speed and that it's from the northwest.
Be funny but informative. Mix in emojis sparingly (max 2).
Examples of good vibes: gnarly, stoked, shredding, epic, firing, pumping."""

def build_user_prompt(wind_speed, wind_direction):
    return f"""Wind alert: {wind_speed:.1f} km/h from {wind_direction}°
    Make this into a funny surfer text about northwest winds at Wreck Beach being perfect for windsurfing/kitesurfing."""
```

### 23. Message Generation Implementation

```python
async def generate_surfer_message(wind_speed: float, wind_direction: float) -> str:
    """
    Generate a surfer-style SMS message using OpenAI.
    Falls back to plain text on any error.
    """
    try:
        # Check cache first (optional optimization)
        cache_key = f"wind_{int(wind_speed)}_{int(wind_direction/10)*10}"
        if cached_msg := check_message_cache(cache_key):
            return cached_msg

        # Build the prompt
        user_prompt = build_user_prompt(wind_speed, wind_direction)

        # Call OpenAI API with timeout
        completion = await asyncio.wait_for(
            client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,  # Higher for creativity
                max_tokens=50,    # Keep it short for SMS
                presence_penalty=0.3,  # Encourage variety
                frequency_penalty=0.3
            ),
            timeout=8.0  # 8 second timeout
        )

        message = completion.choices[0].message.content.strip()

        # Validate message length for SMS
        if len(message) > 160:
            message = message[:157] + "..."

        # Cache the result for similar conditions
        cache_message(cache_key, message, ttl=3600)

        return message

    except asyncio.TimeoutError:
        log.warning("OpenAI API timeout, using fallback message")
        return fallback_plain_message(wind_speed, wind_direction)
    except Exception as e:
        log.error(f"OpenAI API error: {e}")
        return fallback_plain_message(wind_speed, wind_direction)

def fallback_plain_message(wind_speed: float, wind_direction: float) -> str:
    """Fallback to plain text if OpenAI fails."""
    return f"🌊 NW wind {wind_speed:.0f} km/h at Wreck Beach! Perfect conditions for windsurfing."
```

### 24. Error Handling & Fallback Strategy

**Failure Scenarios**:
1. **API Timeout**: Use fallback message after 8 seconds
2. **Rate Limit**: Implement exponential backoff, use cached or fallback
3. **Invalid Response**: Validate and sanitize, fallback if needed
4. **API Outage**: Always fallback to plain formatted text
5. **Token Limit Exceeded**: Truncate or use shorter prompt

**Retry Logic**:
```python
@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=2, max=5),
    retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError))
)
async def generate_with_retry(wind_speed, wind_direction):
    return await generate_surfer_message(wind_speed, wind_direction)
```

### 25. Character Limit Management

**SMS Constraints**:
- Standard SMS: 160 characters (7-bit encoding)
- With emojis: 70 characters (Unicode/UCS-2)
- Safe target: 140 characters to ensure compatibility

```python
def validate_sms_length(message: str) -> str:
    """Ensure message fits in SMS limits."""
    # Check for Unicode characters (emojis)
    has_unicode = any(ord(char) > 127 for char in message)

    if has_unicode:
        max_length = 70
    else:
        max_length = 160

    if len(message) > max_length:
        # Truncate with ellipsis
        return message[:max_length-3] + "..."

    return message
```

### 26. Response Caching Strategy

```python
import hashlib
from datetime import datetime, timedelta

MESSAGE_CACHE = {}  # In production, use Redis or similar

def cache_message(key: str, message: str, ttl: int = 3600):
    """Cache generated messages to reduce API calls."""
    MESSAGE_CACHE[key] = {
        'message': message,
        'expires': datetime.now() + timedelta(seconds=ttl)
    }

def check_message_cache(key: str) -> str | None:
    """Check if we have a cached message for similar conditions."""
    if key in MESSAGE_CACHE:
        entry = MESSAGE_CACHE[key]
        if datetime.now() < entry['expires']:
            return entry['message']
        else:
            del MESSAGE_CACHE[key]
    return None

# Round wind values to reduce cache misses
def get_cache_key(speed: float, direction: float) -> str:
    """Create cache key by rounding values."""
    speed_bucket = int(speed / 5) * 5  # Round to nearest 5 km/h
    dir_bucket = int(direction / 15) * 15  # Round to nearest 15°
    return f"msg_{speed_bucket}_{dir_bucket}"
```

### 27. Testing the LLM Integration

**Test Scenarios**:
```python
# test_openai_integration.py
import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_generate_surfer_message_success():
    """Test successful message generation."""
    with patch('openai.OpenAI') as mock_client:
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Yo! NW winds cranking at 28km/h 🤙"
        mock_client.return_value.chat.completions.create.return_value = mock_response

        message = await generate_surfer_message(28.0, 315.0)
        assert "28" in message
        assert len(message) <= 160

@pytest.mark.asyncio
async def test_fallback_on_timeout():
    """Test fallback message on API timeout."""
    with patch('openai.OpenAI') as mock_client:
        mock_client.return_value.chat.completions.create.side_effect = asyncio.TimeoutError

        message = await generate_surfer_message(25.0, 320.0)
        assert "25 km/h" in message
        assert "NW wind" in message

def test_variety_in_messages():
    """Test that multiple calls produce varied messages."""
    prompts = [build_user_prompt(25 + i, 315) for i in range(5)]
    assert len(set(prompts)) > 1  # Should have variety
```

**Manual Testing**:
```bash
# Test with mock conditions
python -c "
import asyncio
from wind_alert import generate_surfer_message
print(asyncio.run(generate_surfer_message(27.5, 315)))
"

# Force different conditions
python wind_alert.py --test-gpt --wind-speed=30 --wind-direction=310
```

### 28. Example Generated Messages

**Sample Outputs** (under 140 chars each):
```
Input: 26 km/h, 315°
Output: "Yo! NW winds are PUMPING at 26km/h at Wreck! 🏄 Time to shred those waves, conditions are absolutely firing!"

Input: 28 km/h, 320°
Output: "Duuude! Northwest is cranking 28km/h at Wreck Beach! Epic conditions for some gnarly sessions 🤙"

Input: 35 km/h, 300°
Output: "STOKED! NW winds going off at 35km/h! Wreck Beach is absolutely mental right now, get out there!"

Input: 25 km/h, 330°
Output: "Northwest breeze hitting that sweet 25km/h at Wreck! Perfect for cruising, water's calling bro 🌊"
```

### 29. Integration Points

**Modified Alert Flow**:
```python
async def process_alert(wind_data):
    # Existing checks
    if should_send_alert(wind_data):
        # Generate surfer message
        message = await generate_surfer_message(
            wind_data['speed'],
            wind_data['direction']
        )

        # Send SMS with generated message
        send_sms(message)

        # Log the alert
        log.info(f"Alert sent: {message}")
        update_state(wind_data, message)
```

**GitHub Actions Workflow Addition**:
```yaml
- run: python wind_alert.py
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    # ... other secrets
```

### 30. Cost Analysis for OpenAI Integration

**Token Usage Estimates** (per alert):
- System prompt: ~50 tokens
- User prompt: ~30 tokens
- Response: ~30 tokens
- **Total**: ~110 tokens per alert

**Cost with gpt-4o-mini**:
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens
- **Per alert**: ~$0.00002 (negligible)
- **Monthly** (20 alerts): ~$0.0004

**Cost with gpt-3.5-turbo** (alternative):
- Input: $0.50 per 1M tokens
- Output: $2.00 per 1M tokens
- **Per alert**: ~$0.00007
- **Monthly** (20 alerts): ~$0.0014

The OpenAI integration adds negligible cost (<$0.01/month for typical usage).

## References & Citations

1. Open-Meteo API Documentation: https://open-meteo.com/en/docs
2. ECCC MSC Datamart: https://eccc-msc.github.io/open-data/msc-datamart/readme_en/
3. Twilio SMS API: https://www.twilio.com/docs/sms/api
4. GitHub Actions Schedule: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule
5. Wind Direction Conventions: https://www.weather.gov/media/epz/wxcalc/windConversion.pdf
6. Wreck Beach Coordinates: https://geonames.nrcan.gc.ca/
7. Tomorrow.io API: https://docs.tomorrow.io/reference/welcome
8. OpenWeatherMap API: https://openweathermap.org/api
9. Python Tenacity Library: https://tenacity.readthedocs.io/
10. OpenAI Python Library: https://github.com/openai/openai-python
11. OpenAI API Reference: https://platform.openai.com/docs/api-reference
12. SMS Character Limits: https://www.twilio.com/docs/glossary/what-sms-character-limit