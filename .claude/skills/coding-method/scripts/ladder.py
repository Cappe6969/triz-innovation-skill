#!/usr/bin/env python3
"""
Ponytail ladder + Ideal Final Result for a coding task.

The lazy senior dev's decision ladder: YAGNI -> stdlib -> native -> existing
dep -> one line -> minimum code. For a given task this script guesses the
cheapest rung that likely works and states the IFR the task should aim at.
A heuristic MVP, not a verdict — the skill still reasons.

Usage:
    python ladder.py "<task>"      # print the rung + IFR
    python ladder.py ladder        # print the ladder

Standard library only — Python 3.8+.
"""

from __future__ import annotations

import re
import sys
from typing import Callable, Optional

LADDER = [
    ("YAGNI", "Is this needed at all? Trim it — code is a liability."),
    ("stdlib", "Does the language standard library do it? (parsing, sorting, hashing, dates, JSON, CSV, regex…)"),
    ("native", "Does the platform / OS / framework / runtime do it for free?"),
    ("existing-dep", "Does a dependency already do it? Search before you write."),
    ("one-line", "Can it collapse to one idiomatic call? (map/filter/reduce, a builtin, a one-liner)"),
    ("minimum-code", "No lower rung works — write the smallest thing that works and stops."),
]

# Keyword -> rung guess. Longest matches win (sorted by pattern length).
_RUNG_RULES: list[tuple[str, str, str]] = [
    (r"\b(parse|regex|sort(ing)?|date|datetime|json|csv|base64|uuid|hash|hmac|url|math)\b",
     "stdlib", "the standard library covers these operations"),
    (r"\b(files?|os\.|filesystem|network|sockets?|threads?|unicode|encoding)\b",
     "stdlib", "the platform/runtime handles these natively"),
    (r"\b(reuse|existing function|already have|our (module|lib|library|api)|wrap existing)\b",
     "existing-dep", "you likely already own the abstraction"),
    (r"\b(single (call|expression)|one-liner|idiomatic|map|filter|reduce|comprehension)\b",
     "one-line", "this smells like one idiomatic call"),
    (r"\b(build from scratch|new (module|class|library)|greenfield|framework)\b",
     "minimum-code", "you'll have to write something — keep it minimal"),
]


def _guess_rung(task: str) -> tuple[str, str]:
    lower = task.lower()
    for pattern, rung, why in sorted(_RUNG_RULES, key=lambda r: -len(r[0])):
        if re.search(pattern, lower):
            return rung, why
    return "minimum-code", "no signal matches — default to the smallest thing that works"


def suggest_rung(task: str) -> dict:
    """Return {task, rung, why, ifr, almost_ifr} for a task text."""
    rung, why = _guess_rung(task)
    ifr = (
        "The behavior happens by itself — no new code, no new module, no added "
        "complexity — because an existing or deep abstraction already performs it."
    )
    almost_ifr = "Smallest thing that must still be written; state the one-line purpose FIRST, then the body."
    return {
        "task": task,
        "rung": rung,
        "why": why,
        "ifr": ifr,
        "almost_ifr": almost_ifr,
    }


def _print_ladder() -> None:
    for rung, desc in LADDER:
        print(f"[{rung:12}] {desc}")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    argv = sys.argv[1:]
    if not argv:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(1)
    if argv[0] == "ladder":
        _print_ladder()
        sys.exit(0)

    result = suggest_rung(" ".join(argv))
    print(f"Task: {result['task']}")
    print(f"Rung: [{result['rung']}] — {result['why']}")
    print(f"IFR: {result['ifr']}")
    print(f"Almost-IFR: {result['almost_ifr']}")


if __name__ == "__main__":
    main()
