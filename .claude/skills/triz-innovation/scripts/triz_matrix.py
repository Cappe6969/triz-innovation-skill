#!/usr/bin/env python3
"""
TRIZ Contradiction Matrix — 39×39 Altshuller matrix lookup.

Looks up inventive principles for an engineering contradiction
(improve parameter X → worsens parameter Y) using the bundled 39×39 matrix.
Returns ranked principles with parameter names.

Usage:
    python triz_matrix.py <improving_id> <worsening_id>
    python triz_matrix.py --list              # list the 39 parameters
    python triz_matrix.py                     # print usage

Standard library only — Python 3.9+.
"""

from __future__ import annotations

import sys
import csv
from pathlib import Path
from typing import Any


def _data_dir() -> Path:
    """Path to the bundled data directory, relative to this script."""
    return Path(__file__).resolve().parent / "data"


def load_parameters() -> dict[int, str]:
    """Return {id: name} from parameters_39.csv."""
    params: dict[int, str] = {}
    path = _data_dir() / "parameters_39.csv"
    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            params[int(row["id"])] = row["name"].strip()
    return params


def load_principles() -> dict[int, str]:
    """Return {id: name} from inventive_principles.csv."""
    principles: dict[int, str] = {}
    path = _data_dir() / "inventive_principles.csv"
    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            principles[int(row["id"])] = row["name"].strip()
    return principles


def load_matrix() -> dict[tuple[int, int], list[int]]:
    """Return {(improving, worsening): [principle_id, ...]} from the matrix CSV.

    Principle IDs are parsed from the semicolon-separated 'principles' column.
    Empty / whitespace-only cells produce an empty list.
    """
    path = _data_dir() / "contradiction_matrix.csv"
    matrix: dict[tuple[int, int], list[int]] = {}
    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            key = (int(row["improving"]), int(row["worsening"]))
            principles_str = row["principles"].strip()
            if principles_str:
                pids = [int(p.strip()) for p in principles_str.split(";") if p.strip()]
            else:
                pids = []
            matrix[key] = pids
    return matrix


def lookup(improving: int, worsening: int) -> dict[str, Any]:
    """Look up inventive principles for an engineering contradiction.

    Args:
        improving: ID of the parameter to improve (1..39).
        worsening: ID of the parameter that worsens as a result (1..39).

    Returns:
        dict with keys:
        - "improving": {"id": int, "name": str}
        - "worsening": {"id": int, "name": str}
        - "principles": list of {"id": int, "name": str}
        - "note": str or None

    Raises:
        ValueError: if either argument is not an int (including bool) or outside 1..39.
    """
    # R6.2: Reject non-int including bool
    if not isinstance(improving, int) or isinstance(improving, bool) or not (1 <= improving <= 39):
        raise ValueError(
            f"Improving parameter id must be an integer in 1..39, "
            f"got {improving!r} (type={type(improving).__name__})"
        )
    if not isinstance(worsening, int) or isinstance(worsening, bool) or not (1 <= worsening <= 39):
        raise ValueError(
            f"Worsening parameter id must be an integer in 1..39, "
            f"got {worsening!r} (type={type(worsening).__name__})"
        )

    params = load_parameters()
    principles_map = load_principles()
    matrix = load_matrix()

    result: dict[str, Any] = {
        "improving": {"id": improving, "name": params[improving]},
        "worsening": {"id": worsening, "name": params[worsening]},
        "principles": [],
        "note": None,
    }

    # Same parameter on both sides → physical contradiction, not engineering
    if improving == worsening:
        result["note"] = (
            "Same parameter on both sides — see "
            "references/physical-contradictions.md "
            "(separate in time/space/condition)."
        )
        return result

    principle_ids = matrix.get((improving, worsening), [])

    if not principle_ids:
        result["note"] = (
            "No matrix entry for this parameter pair — "
            "try Resource Analysis + IFR as fallback."
        )
        return result

    result["principles"] = [
        {"id": pid, "name": principles_map[pid]} for pid in principle_ids
    ]

    return result


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python triz_matrix.py <improving_id> <worsening_id>",
            file=sys.stderr,
        )
        print(
            "       python triz_matrix.py --list",
            file=sys.stderr,
        )
        print(
            "\nHint: run 'python triz_matrix.py --list' to see the 39 parameters.",
            file=sys.stderr,
        )
        sys.exit(1)

    if sys.argv[1] == "--list":
        params = load_parameters()
        for pid in sorted(params):
            print(f"{pid:>2}  {params[pid]}")
        return

    if len(sys.argv) < 3:
        print(
            "Usage: python triz_matrix.py <improving_id> <worsening_id>",
            file=sys.stderr,
        )
        print(
            "Hint: run 'python triz_matrix.py --list' to see the 39 parameters.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        improving = int(sys.argv[1])
        worsening = int(sys.argv[2])
    except ValueError:
        print(
            "Error: both arguments must be integers in 1..39.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        result = lookup(improving, worsening)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Improving: {result['improving']['name']} (id={result['improving']['id']})")
    print(f"Worsening: {result['worsening']['name']} (id={result['worsening']['id']})")
    print()

    if result["principles"]:
        print("Recommended Inventive Principles:")
        for p in result["principles"]:
            print(f"  {p['id']:>2}. {p['name']}")
    else:
        print("Recommended Inventive Principles: (none)")

    if result["note"]:
        print(f"\nNote: {result['note']}")


if __name__ == "__main__":
    main()
