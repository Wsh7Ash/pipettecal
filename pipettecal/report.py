"""Report building for pipettecal."""

from __future__ import annotations

import json
from typing import Any

from .model import Problem
from .calibrate import CalibResult


def build_report(problem: Problem, result: CalibResult) -> dict[str, Any]:
    inp = {
        "target_volume": problem.target_volume,
        "unit": problem.unit,
        "tolerance_percent": problem.tolerance_percent,
        "max_cv_percent": problem.max_cv_percent,
        "measurements": [{"mass_g": m.mass_g, "temperature_c": m.temperature_c} for m in problem.measurements],
        "air_density_g_ml": problem.air_density_g_ml,
        "weight_density_g_ml": problem.weight_density_g_ml,
    }
    return {
        "input": inp,
        "status": result.status,
        "replicates_ml": result.replicates_ml,
        "mean_ml": result.mean_ml,
        "std_ml": result.std_ml,
        "cv_percent": result.cv_percent,
        "error_percent": result.error_percent,
        "tolerance_percent": result.tolerance_percent,
        "max_cv_percent": result.max_cv_percent,
        "reasons": result.reasons,
    }


def render_text(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"status: {report['status']}")
    lines.append(f"target: {report['input']['target_volume']} {report['input']['unit']}")
    lines.append(f"mean delivered: {report['mean_ml'] * 1000:.4f} uL ({report['mean_ml']:.6f} mL)")
    lines.append(f"std: {report['std_ml'] * 1000:.4f} uL")
    lines.append(f"CV: {report['cv_percent']:.4f}%")
    lines.append(f"systematic error: {report['error_percent']:.4f}%")
    lines.append(f"replicates: {len(report['replicates_ml'])}")
    for i, v in enumerate(report["replicates_ml"]):
        lines.append(f"  {i+1}: {v*1000:.4f} uL")
    if report["reasons"]:
        lines.append("reasons:")
        for r in report["reasons"]:
            lines.append(f"  - {r}")
    return "\n".join(lines) + "\n"


def dump_json(path, report):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write("\n")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
