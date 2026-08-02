#!/usr/bin/env python3
"""Create deterministic randomized A/B packets without revealing arm names."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--answer-key", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    grouped = {}
    for result in args.results_dir.glob("*/result.json"):
        data = json.loads(result.read_text(encoding="utf-8"))
        grouped.setdefault(data["fixture"], {})[data["arm"]] = result.parent
    rng = random.Random(args.seed)
    packets = []
    answer_key = {}
    for fixture in sorted(grouped):
        arms = grouped[fixture]
        if set(arms) != {"baseline", "treatment"}:
            raise ValueError("both arms required for " + fixture)
        order = ["baseline", "treatment"]
        rng.shuffle(order)
        packet_id = hashlib.sha256((fixture + str(args.seed)).encode()).hexdigest()[:12]
        candidates = []
        for label, arm in zip(("A", "B"), order):
            folder = arms[arm]
            candidates.append({
                "label": label,
                "patch": (folder / "patch.diff").read_text(encoding="utf-8"),
                "tests": (folder / "tests.txt").read_text(encoding="utf-8"),
            })
            answer_key[label + ":" + packet_id] = arm
        packets.append({"packet_id": packet_id, "fixture": fixture, "candidates": candidates, "rubric": ["correctness", "minimality", "clarity", "dependency justification"], "preferred": None})
    args.output.write_text(json.dumps({"packets": packets}, indent=2) + "\n", encoding="utf-8")
    args.answer_key.write_text(json.dumps(answer_key, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
