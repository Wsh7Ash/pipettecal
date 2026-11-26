"""CLI for pipettecal."""

from __future__ import annotations

import argparse
import json
import sys

from .model import load_problem_file, ModelError
from .calibrate import calibrate, verify
from .report import build_report, dump_json, load_json, render_text


def cmd_calibrate(args):
    try:
        problem = load_problem_file(args.input)
    except (ModelError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    result = calibrate(problem)
    report = build_report(problem, result)
    if args.output:
        dump_json(args.output, report)
    print(render_text(report))
    return 0 if result.status == "pass" else 1


def cmd_verify(args):
    try:
        report = load_json(args.report)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    try:
        from .model import load_problem
        problem = load_problem(report["input"])
    except Exception as e:
        print(f"error: invalid embedded input: {e}", file=sys.stderr)
        return 2
    ok, errors = verify(problem, report)
    if ok:
        print("verify: OK")
        return 0
    for e in errors:
        print(f"verify: {e}", file=sys.stderr)
    return 1


def cmd_demo(args):
    import os, tempfile
    sample = {
        "target_volume": 1000.0,
        "unit": "uL",
        "tolerance_percent": 1.0,
        "max_cv_percent": 0.5,
        "measurements": [
            {"mass_g": 0.9985, "temperature_c": 21.0},
            {"mass_g": 0.9991, "temperature_c": 21.2},
            {"mass_g": 0.9979, "temperature_c": 21.1},
            {"mass_g": 0.9988, "temperature_c": 21.3},
        ],
    }
    d = tempfile.mkdtemp()
    inp = os.path.join(d, "in.json")
    out = os.path.join(d, "out.json")
    with open(inp, "w") as f:
        json.dump(sample, f)
    rc = cmd_calibrate(argparse.Namespace(input=inp, output=out))
    if rc not in (0, 1):
        return rc
    return cmd_verify(argparse.Namespace(report=out))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pipettecal")
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("calibrate")
    c.add_argument("input")
    c.add_argument("-o", "--output")
    c.set_defaults(func=cmd_calibrate)
    v = sub.add_parser("verify")
    v.add_argument("report")
    v.set_defaults(func=cmd_verify)
    d = sub.add_parser("demo")
    d.set_defaults(func=cmd_demo)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
