# Usage — pipettecal

## Input
```json
{
  "target_volume": 1000.0,
  "unit": "uL",
  "tolerance_percent": 1.0,
  "max_cv_percent": 0.5,
  "measurements": [{"mass_g": 0.9985, "temperature_c": 21.0}]
}
```

## Commands
- `python -m pipettecal calibrate INPUT [-o OUT]`
- `python -m pipettecal verify REPORT`
- `python -m pipettecal demo`