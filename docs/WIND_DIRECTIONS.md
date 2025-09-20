# Wind Direction Configuration

## Alert-Triggering Wind Directions

The system now alerts for winds from the following directions when speed ≥ 25 km/h:

### Primary Directions (Good for Windsurfing/Kitesurfing at Wreck Beach)

1. **North (N)**: 337.5° to 22.5°
   - Pure North: 0°/360°
   - NNW: 337.5° to 348.75°
   - NNE: 11.25° to 22.5°

2. **Northwest (NW)**: 292.5° to 337.5°
   - WNW: 292.5° to 303.75°
   - Pure NW: 315°
   - NNW: 326.25° to 337.5°

3. **West (W)**: 247.5° to 292.5°
   - WSW: 247.5° to 258.75°
   - Pure West: 270°
   - WNW: 281.25° to 292.5°

### Combined Alert Range
**Total coverage: 247.5° through 22.5° (via 360°)**

This covers approximately 135 degrees of the compass, or about 37.5% of all possible wind directions.

## Non-Alert Directions

The system will NOT alert for winds from:
- East (E): 78.75° to 101.25°
- Southeast (SE): 123.75° to 146.25°
- South (S): 168.75° to 191.25°
- Southwest (SW): 213.75° to 236.25°
- And all variations between 22.5° and 247.5°

## Testing Examples

### Will Alert ✅
```bash
python wind_alert.py --dry-run --test-wind-speed=25 --test-wind-direction=0      # N
python wind_alert.py --dry-run --test-wind-speed=25 --test-wind-direction=270    # W
python wind_alert.py --dry-run --test-wind-speed=25 --test-wind-direction=315    # NW
python wind_alert.py --dry-run --test-wind-speed=25 --test-wind-direction=250    # WSW
python wind_alert.py --dry-run --test-wind-speed=25 --test-wind-direction=10     # N
```

### Won't Alert ❌
```bash
python wind_alert.py --dry-run --test-wind-speed=25 --test-wind-direction=90     # E
python wind_alert.py --dry-run --test-wind-speed=25 --test-wind-direction=180    # S
python wind_alert.py --dry-run --test-wind-speed=25 --test-wind-direction=135    # SE
python wind_alert.py --dry-run --test-wind-speed=25 --test-wind-direction=225    # SW
```

## Why These Directions?

For Wreck Beach in Vancouver:
- **North winds**: Clean offshore winds, great for windsurfing
- **Northwest winds**: Most consistent and reliable for water sports
- **West winds**: Good side-shore conditions

The flexibility (±22.5° from center) ensures you get alerted even when winds are slightly off the perfect direction but still good enough for water sports.