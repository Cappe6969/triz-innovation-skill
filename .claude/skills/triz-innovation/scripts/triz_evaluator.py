#!/usr/bin/env python3
"""
TRIZ solution evaluator — scores candidate solutions 1–5 on eight criteria
and produces a sorted monospaced table.

Usage:
    python triz_evaluator.py solutions.csv   # read CSV, print sorted table
    python triz_evaluator.py                 # demo mode with built-in sample
    python triz_evaluator.py --help          # print CSV format

CSV header (case-insensitive, aliases accepted):
    solution,impact,feasibility,cost,speed,risk,reversibility,complexity,ideality
    (Legacy headers affordability/safety/simplicity also accepted.)

Standard library only — Python 3.9+.
"""

from __future__ import annotations

import sys
import csv
import io
from typing import Any

CRITERIA = [
    "impact",
    "feasibility",
    "cost",
    "speed",
    "risk",
    "reversibility",
    "complexity",
    "ideality",
]

_CRITERIA_ALIASES = {
    "affordability": "cost",
    "safety": "risk",
    "simplicity": "complexity",
}


def _validate_criterion(name: str, value: Any) -> None:
    """Validate a single criterion value. Raises ValueError on invalid input."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(
            f"Criterion '{name}' must be an integer 1–5, "
            f"got {type(value).__name__}: {value!r}"
        )
    if value < 1 or value > 5:
        raise ValueError(
            f"Criterion '{name}' must be 1–5, got {value}"
        )


_SAMPLE_DATA: list[dict[str, Any]] = [
    {
        "solution": "Phone-based exercise reminders with gamification",
        "impact": 4,
        "feasibility": 3,
        "cost": 2,
        "speed": 4,
        "risk": 3,
        "reversibility": 5,
        "complexity": 2,
        "ideality": 3,
    },
    {
        "solution": "Therapist-led weekly check-in calls",
        "impact": 5,
        "feasibility": 3,
        "cost": 1,
        "speed": 2,
        "risk": 4,
        "reversibility": 4,
        "complexity": 4,
        "ideality": 2,
    },
    {
        "solution": "Peer-support group chat with shared progress board",
        "impact": 3,
        "feasibility": 4,
        "cost": 4,
        "speed": 3,
        "risk": 3,
        "reversibility": 5,
        "complexity": 2,
        "ideality": 4,
    },
    {
        "solution": "AI-driven adaptive exercise plan with minimal notifications",
        "impact": 5,
        "feasibility": 2,
        "cost": 2,
        "speed": 3,
        "risk": 2,
        "reversibility": 3,
        "complexity": 1,
        "ideality": 4,
    },
]


def score(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Score a list of solution dicts.

    Each input row must have a "solution" key (str) plus the eight criteria
    as ints 1–5: impact, feasibility, cost, speed, risk, reversibility,
    complexity, ideality.

    Returns a new list of dicts with an added "total" key (sum of eight criteria),
    sorted by total descending. Raises ValueError for missing or invalid criteria.
    """
    scored = []
    for row in rows:
        entry = dict(row)
        for c in CRITERIA:
            if c not in entry:
                raise ValueError(
                    f"Missing criterion '{c}' in row: {entry.get('solution', '?')}"
                )
            _validate_criterion(c, entry[c])
        total = sum(int(entry[c]) for c in CRITERIA)
        entry["total"] = total
        scored.append(entry)
    scored.sort(key=lambda r: r["total"], reverse=True)
    return scored


def format_table(scored: list[dict[str, Any]]) -> str:
    """Format scored solutions as a monospaced markdown/ASCII table.

    Columns: solution, impact, feasibility, cost, speed, risk,
             reversibility, complexity, ideality, total.
    """
    headers = [
        "Solution", "Impact", "Feasibility", "Cost", "Speed",
        "Risk", "Reversibility", "Complexity", "Ideality", "Total",
    ]
    col_keys = ["solution"] + CRITERIA + ["total"]

    # Calculate column widths
    widths: list[int] = []
    for i, h in enumerate(headers):
        max_w = len(h)
        for row in scored:
            val = str(row.get(col_keys[i], ""))
            max_w = max(max_w, len(val))
        widths.append(max_w)

    def _row(values: list[str]) -> str:
        cells = [v.ljust(w) for v, w in zip(values, widths)]
        return "| " + " | ".join(cells) + " |"

    def _sep() -> str:
        parts = ["-" * w for w in widths]
        return "|-" + "-|-".join(parts) + "-|"

    lines: list[str] = []
    lines.append(_row(headers))
    lines.append(_sep())
    for row in scored:
        values = [str(row.get(k, "")) for k in col_keys]
        lines.append(_row(values))

    return "\n".join(lines)


def _parse_csv(filepath: str) -> list[dict[str, Any]]:
    """Parse a solutions CSV, validating scores. Accepts canonical and legacy header names."""
    expected_header = ["solution"] + CRITERIA
    rows: list[dict[str, Any]] = []

    try:
        fh = open(filepath, "r", encoding="utf-8-sig", newline="")
    except FileNotFoundError:
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: cannot read file: {e}", file=sys.stderr)
        sys.exit(1)

    with fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            print("Error: CSV file appears to be empty or has no header.", file=sys.stderr)
            sys.exit(1)

        # Normalize fieldnames and apply aliases
        actual_raw = [f.strip() for f in reader.fieldnames]
        actual = []
        for f in actual_raw:
            fl = f.lower()
            actual.append(_CRITERIA_ALIASES.get(fl, fl))
        norm_actual = [f.lower() for f in actual]

        if norm_actual != expected_header:
            print(f"Error: unexpected CSV header.", file=sys.stderr)
            print(f"  Expected: {','.join(expected_header)}", file=sys.stderr)
            print(f"  Got:      {','.join(actual_raw)}", file=sys.stderr)
            sys.exit(1)

        for line_num, raw_row in enumerate(reader, start=2):  # header is line 1
            # Check for missing fields
            if any(k not in raw_row or raw_row[k] is None for k in reader.fieldnames):
                missing = [k for k in reader.fieldnames if k not in raw_row or raw_row[k] is None]
                print(
                    f"Error: row {line_num}: missing value for column(s): {', '.join(missing)}",
                    file=sys.stderr,
                )
                sys.exit(1)

            row: dict[str, Any] = {}
            for k, v in raw_row.items():
                key = k.strip().lower()
                key = _CRITERIA_ALIASES.get(key, key)
                row[key] = v.strip() if isinstance(v, str) else v

            solution_label = row.get("solution", f"row-{line_num}")
            for crit in CRITERIA:
                val_str = str(row.get(crit, "")).strip()
                try:
                    val = int(val_str)
                except (ValueError, TypeError):
                    print(
                        f"Error: row {line_num} ('{solution_label}'): "
                        f"'{crit}' value '{val_str}' is not a valid integer.",
                        file=sys.stderr,
                    )
                    sys.exit(1)
                try:
                    _validate_criterion(crit, val)
                except ValueError as e:
                    print(
                        f"Error: row {line_num} ('{solution_label}'): {e}",
                        file=sys.stderr,
                    )
                    sys.exit(1)
                row[crit] = val
            rows.append(row)

    return rows


def _print_help() -> None:
    print("TRIZ Evaluator — CSV format")
    print()
    print("CSV header (case-insensitive, legacy aliases accepted):")
    print("  solution,impact,feasibility,cost,speed,risk,reversibility,complexity,ideality")
    print("  (affordability→cost, safety→risk, simplicity→complexity)")
    print()
    print("All eight criteria use a 1–5 scale where 5 = best, 1 = worst:")
    print("  impact         — 5 = highest positive impact")
    print("  feasibility    — 5 = most feasible to implement")
    print("  cost           — 5 = most affordable (lowest cost)")
    print("  speed          — 5 = fastest to implement")
    print("  risk           — 5 = safest (lowest risk)")
    print("  reversibility  — 5 = easiest to reverse/roll back")
    print("  complexity     — 5 = simplest (lowest complexity)")
    print("  ideality       — 5 = closest to ideal final result")
    print()
    print("Scoring: total = sum of all eight criteria (max 40).")
    print()
    print("Example CSV content:")
    print("  solution,impact,feasibility,cost,speed,risk,reversibility,complexity,ideality")
    print("  Gamified reminders,4,3,2,4,3,5,2,3")
    print("  Therapist calls,5,3,1,2,4,4,4,2")


def main() -> None:
    # R12: Windows-safe stdout
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    if len(sys.argv) < 2:
        # Demo mode
        print("TRIZ Evaluator — demo mode (built-in sample)")
        print()
        scored = score(_SAMPLE_DATA)
        print(format_table(scored))
        return

    arg = sys.argv[1]
    if arg == "--help" or arg == "-h":
        _print_help()
        return

    # Assume it's a CSV file path
    rows = _parse_csv(arg)

    scored = score(rows)
    print(format_table(scored))


if __name__ == "__main__":
    main()
