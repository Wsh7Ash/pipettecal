# pipettecal

Gravimetric pipette calibration certificate. Given a target volume and a set
of replicate weighings (with temperature), compute each replicate's delivered
volume with a buoyancy correction, then the mean, sample standard deviation,
coefficient of variation, and systematic error, and judge pass/fail against
tolerances. Every certificate embeds its input so an independent command can
re-derive and verify it.

## Features

- Buoyancy-corrected delivered volume per replicate (water density by
  temperature, air and weight densities).
- Mean, sample std, CV%, systematic error%.
- Pass/fail against tolerance and max-CV thresholds with reasons.
- Independent `verify` command re-derives all numbers.

## Requirements

Python 3.11+. Standard library only.

## Quick start

```bash
python -m pipettecal demo
python -m pipettecal calibrate examples/sample.json -o report.json
python -m pipettecal verify report.json
```

## Limitations

- Water density is a polynomial approximation (valid ~0-40 C).
- Does not model evaporation, operator technique, or balance calibration.
- Educational/QA aid, not a certified calibration procedure.