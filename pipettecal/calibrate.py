"""Gravimetric calibration computation for pipettecal."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .model import Problem, water_density_g_ml


@dataclass
class CalibResult:
    status: str  # "pass" | "fail"
    replicates_ml: list[float]
    mean_ml: float
    std_ml: float  # sample std
    cv_percent: float
    error_percent: float
    tolerance_percent: float
    max_cv_percent: float
    reasons: list[str]
    nodes: int = 0


def calibrate(problem: Problem) -> CalibResult:
    rho_a = problem.air_density_g_ml
    rho_wt = problem.weight_density_g_ml
    reps: list[float] = []
    for m in problem.measurements:
        rho_w = water_density_g_ml(m.temperature_c)
        # buoyancy-corrected delivered volume (mL)
        v = m.mass_g * (1.0 - rho_a / rho_wt) / (rho_w - rho_a)
        reps.append(v)

    n = len(reps)
    mean = sum(reps) / n
    var = sum((x - mean) ** 2 for x in reps) / (n - 1) if n > 1 else 0.0
    std = math.sqrt(var)
    cv = (std / mean * 100.0) if mean != 0 else float("inf")
    target = problem.target_ml
    error = (mean - target) / target * 100.0 if target != 0 else float("inf")

    reasons: list[str] = []
    if abs(error) > problem.tolerance_percent:
        reasons.append(f"systematic error {error:.3f}% exceeds tolerance {problem.tolerance_percent}%")
    if cv > problem.max_cv_percent:
        reasons.append(f"CV {cv:.3f}% exceeds max {problem.max_cv_percent}%")
    status = "pass" if not reasons else "fail"
    return CalibResult(
        status=status,
        replicates_ml=reps,
        mean_ml=mean,
        std_ml=std,
        cv_percent=cv,
        error_percent=error,
        tolerance_percent=problem.tolerance_percent,
        max_cv_percent=problem.max_cv_percent,
        reasons=reasons,
    )


def verify(problem: Problem, report: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []
    # rebuild problem from embedded input
    try:
        from .model import load_problem
        p_check = load_problem(report["input"])
    except Exception as e:
        return False, [f"invalid embedded input: {e}"]
    if p_check.target_volume != problem.target_volume or p_check.unit != problem.unit:
        errors.append("embedded target/unit differ")
    if len(p_check.measurements) != len(problem.measurements):
        errors.append("measurement count differs")
    # recompute
    res = calibrate(problem)
    # check replicates
    rep_reps = report.get("replicates_ml")
    if not isinstance(rep_reps, list) or len(rep_reps) != len(res.replicates_ml):
        errors.append("replicates_ml missing or wrong length")
    else:
        for i, (a, b) in enumerate(zip(rep_reps, res.replicates_ml)):
            if abs(float(a) - b) > 1e-9:
                errors.append(f"replicate {i} mismatch")
    if abs(float(report.get("mean_ml", 0)) - res.mean_ml) > 1e-9:
        errors.append("mean_ml mismatch")
    if abs(float(report.get("std_ml", 0)) - res.std_ml) > 1e-9:
        errors.append("std_ml mismatch")
    if abs(float(report.get("cv_percent", 0)) - res.cv_percent) > 1e-9:
        errors.append("cv_percent mismatch")
    if abs(float(report.get("error_percent", 0)) - res.error_percent) > 1e-9:
        errors.append("error_percent mismatch")
    if report.get("status") != res.status:
        errors.append(f"status mismatch: reported {report.get('status')}, recomputed {res.status}")
    return (len(errors) == 0), errors
