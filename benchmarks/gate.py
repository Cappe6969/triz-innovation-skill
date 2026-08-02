#!/usr/bin/env python3
"""Evaluate the documented ten-fixture release gate."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_dir", type=Path)
    parser.add_argument("reviews", type=Path)
    parser.add_argument("answer_key", type=Path)
    args = parser.parse_args()
    results = [json.loads(path.read_text(encoding="utf-8")) for path in args.results_dir.glob("*/result.json")]
    by_fixture = {}
    for result in results:
        by_fixture.setdefault(result["fixture"], {})[result["arm"]] = result
    if len(by_fixture) != 10 or any(set(arms) != {"baseline", "treatment"} for arms in by_fixture.values()):
        raise SystemExit("GATE FAIL: ten complete paired fixtures are required")
    treatment_passes = sum(arms["treatment"]["tests_exit"] == 0 for arms in by_fixture.values())
    no_regressions = all(not (arms["baseline"]["tests_exit"] == 0 and arms["treatment"]["tests_exit"] != 0) for arms in by_fixture.values())
    baseline_lines = [arms["baseline"]["production_lines_added"] for arms in by_fixture.values()]
    treatment_lines = [arms["treatment"]["production_lines_added"] for arms in by_fixture.values()]
    no_dependencies = all(not arms["treatment"]["dependencies_added"] for arms in by_fixture.values())
    reviews = json.loads(args.reviews.read_text(encoding="utf-8"))["packets"]
    key = json.loads(args.answer_key.read_text(encoding="utf-8"))
    preferred = 0
    for packet in reviews:
        label = packet.get("preferred")
        if label in ("A", "B") and key.get(label + ":" + packet["packet_id"]) == "treatment":
            preferred += 1
    report = {
        "treatment_tests": f"{treatment_passes}/10",
        "no_regressions": no_regressions,
        "blind_treatment_preference": f"{preferred}/10",
        "median_baseline_production_lines": statistics.median(baseline_lines),
        "median_treatment_production_lines": statistics.median(treatment_lines),
        "no_unjustified_dependencies": no_dependencies,
    }
    passed = treatment_passes == 10 and no_regressions and preferred >= 7 and statistics.median(treatment_lines) <= statistics.median(baseline_lines) and no_dependencies
    report["passed"] = passed
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
