"""Input parsing and validation for pipettecal."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import Any


class ModelError(ValueError):
    pass


@dataclass
class Measurement:
    mass_g: float
    temperature_c: float


@dataclass
class Problem:
    target_volume: float  # in `unit`
    unit: str  # "uL" or "mL"
    tolerance_percent: float
    max_cv_percent: float
    measurements: list[Measurement]
    air_density_g_ml: float = 0.0012
    weight_density_g_ml: float = 8.0

    @property
    def target_ml(self) -> float:
        if self.unit == "uL":
            return self.target_volume / 1000.0
        if self.unit == "mL":
            return self.target_volume
        raise ValueError(self.unit)


def water_density_g_ml(temp_c: float) -> float:
    """Water density (g/mL) for 0-40 C, polynomial approximation."""
    t = temp_c
    # Kell-like polynomial (g/cm^3)
    return (0.9998395 + 6.798299e-5 * t - 9.101827e-6 * t * t
            + 1.001685e-7 * t ** 3 - 1.120083e-9 * t ** 4
            + 6.536332e-12 * t ** 5)


def load_problem(data: Any) -> Problem:
    if not isinstance(data, dict):
        raise ModelError("input must be a JSON object")
    tv = data.get("target_volume")
    _req_num(tv, "target_volume")
    _req(tv > 0, "target_volume must be positive")
    unit = data.get("unit", "uL")
    if unit not in ("uL", "mL"):
        raise ModelError("unit must be 'uL' or 'mL'")
    tol = data.get("tolerance_percent", 1.0)
    _req_num(tol, "tolerance_percent")
    _req(tol >= 0, "tolerance_percent must be >= 0")
    cv = data.get("max_cv_percent", 0.5)
    _req_num(cv, "max_cv_percent")
    _req(cv >= 0, "max_cv_percent must be >= 0")
    meas_raw = data.get("measurements")
    if not isinstance(meas_raw, list) or len(meas_raw) < 2:
        raise ModelError("measurements must be a list of at least 2")
    meas: list[Measurement] = []
    for i, m in enumerate(meas_raw):
        if not isinstance(m, dict):
            raise ModelError(f"measurements[{i}] must be an object")
        mass = m.get("mass_g")
        temp = m.get("temperature_c")
        _req_num(mass, f"measurements[{i}].mass_g")
        _req_num(temp, f"measurements[{i}].temperature_c")
        _req(mass >= 0, f"measurements[{i}].mass_g must be >= 0")
        _req(0 <= temp <= 40, f"measurements[{i}].temperature_c out of range 0-40")
        meas.append(Measurement(mass_g=float(mass), temperature_c=float(temp)))
    ad = data.get("air_density_g_ml", 0.0012)
    wd = data.get("weight_density_g_ml", 8.0)
    _req_num(ad, "air_density_g_ml")
    _req_num(wd, "weight_density_g_ml")
    return Problem(target_volume=float(tv), unit=unit, tolerance_percent=float(tol),
                   max_cv_percent=float(cv), measurements=meas,
                   air_density_g_ml=float(ad), weight_density_g_ml=float(wd))


def _req(cond, msg):
    if not cond:
        raise ModelError(msg)


def _req_num(x, name):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise ModelError(f"{name} must be a number")
    if not math.isfinite(x):
        raise ModelError(f"{name} must be finite")


def load_problem_file(path: str) -> Problem:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return load_problem(data)
