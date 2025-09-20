# Testing Commands for Wind Alert System

## Test Commands

### 1. Dry Run Mode
Test without sending actual SMS:
```bash
python wind_alert.py --dry-run
```

### 2. Force Alert with Test Data
Test with NW wind at 30 km/h (meets criteria):
```bash
python wind_alert.py --dry-run --force-alert --test-wind-speed 30 --test-wind-direction 315
```

### 3. Test Non-Alert Condition
Test with wind that doesn't meet criteria (not NW):
```bash
python wind_alert.py --dry-run --test-wind-speed 30 --test-wind-direction 180
```

### 4. Test Below Threshold
Test with NW wind below threshold:
```bash
python wind_alert.py --dry-run --test-wind-speed 20 --test-wind-direction 315
```

### 5. Test Boundary Conditions
Test NW boundary (292.5°):
```bash
python wind_alert.py --dry-run --test-wind-speed 26 --test-wind-direction 292.5
```

Test NW boundary (337.5°):
```bash
python wind_alert.py --dry-run --test-wind-speed 26 --test-wind-direction 337.5
```

### 6. Test with Real Weather Data
Fetch actual weather data (dry run):
```bash
python wind_alert.py --dry-run
```

### 7. Production Test (with SMS)
Send actual SMS with test data (requires .env configuration):
```bash
python wind_alert.py --force-alert --test-wind-speed 27 --test-wind-direction 320
```

## Verify Installation

Check all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Check Configuration

Verify .env file exists and is configured:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## View Logs

Logs are written to:
- Console output
- `/tmp/wind_alert.log`

View log file:
```bash
tail -f /tmp/wind_alert.log
```

## Check State File

View current alert state:
```bash
cat /tmp/wind_alert_state.json
```