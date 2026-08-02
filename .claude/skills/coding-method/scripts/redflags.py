#!/usr/bin/env python3
"""
Red-flag review checklist for the coding-method skill.

Prints the review checklist (Ousterhout red flags + construction filters) and,
given a file, scans for the smells that are mechanically detectable. The full
catalogue lives in references/red-flags.md; this script is the fast CLI pass.

Usage:
    python redflags.py              # print the checklist only
    python redflags.py <file>       # print checklist + scan the file

Standard library only — Python 3.8+.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

CHECKLIST = [
    # Deep modules (Ousterhout)
    "Shallow module — interface costs as much as the functionality it provides?",
    "Information leakage — a design decision reflected in multiple modules?",
    "Pass-through method / pass-through variable threaded across layers?",
    "Repetition — same pattern copied (DRY), or comment repeats code?",
    "Special-general mixture — one-off glue mixed into a general module?",
    "Conjoined methods — one method is only called by one other (better together)?",
    "Vague / hard-to-pick name — does the name create an image?",
    "Nonobvious code — a quick guess is not confident? Document the why.",
    # Construction filters (Code Complete)
    "Loose coupling / high cohesion — small clear fan-out, internals strongly related?",
    "Secrets hidden behind a minimal stable interface (information hiding)?",
    "Leanness — could anything more be taken away without losing a function?",
    "Complexity managed — can a reader hold each part in isolation?",
    # Pragmatics (Pragmatic Programmer / SICP)
    "DRY / orthogonality — is each piece of knowledge single-sourced?",
    "Abstraction barrier — callers insulated from representation changes?",
    "Broken windows — any rot left in place that will grow?",
    # TRIZ
    "Trimming candidate — a component whose useful function could move elsewhere?",
    "Complexity relocated — did the fix just move the mess, not remove it?",
]

_SMELL_RULES = [
    ("long-params", r"def\s+\w+\([^)]*(?:,\s*[^)]*){5,}\)", "function with 6+ parameters"),
    ("long-lines", r".{101,}", "line longer than 100 characters"),
    ("markers", r"\b(TODO|FIXME|HACK|XXX)\b", "TODO/FIXME/HACK marker"),
]

INDENT_RE = "    "  # nominal indentation unit for nesting heuristics


def scan(file_path: Optional[str] = None) -> dict:
    """Return {summary, checklist, findings} for the given file (or checklist only)."""
    result = {
        "summary": "Review checklist (fast pass):",
        "checklist": list(CHECKLIST),
        "findings": [],
    }
    if not file_path:
        return result

    path = Path(file_path)
    if not path.is_file():
        result["findings"].append(f"file not found: {path}")
        return result

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        result["findings"].append(f"cannot read {path}: {exc}")
        return result

    import re

    defs = [(i, line) for i, line in enumerate(lines) if re.match(r"\s*def\s+\w+\(", line)]

    for name, pattern, desc in _SMELL_RULES:
        found = [(i + 1, line) for i, line in enumerate(lines) if re.search(pattern, line)]
        if found:
            result["findings"].append(
                f"{desc}: {len(found)} hit(s) — first at line {found[0][0]}: "
                + found[0][1].strip()[:72]
            )

    # Function-length heuristic: lines spanned by each def block.
    for i, (line_idx, line) in enumerate(defs):
        end = defs[i + 1][0] if i + 1 < len(defs) else len(lines)
        span = end - line_idx
        if span > 60:
            name = line.strip()
            result["findings"].append(
                f"long function ({span} lines): line {line_idx + 1}: {name[:60]}"
            )

    # Max indentation depth heuristic (approximate nesting).
    depth = 0
    for line in lines:
        stripped = line.lstrip(" ")
        if not stripped or stripped.startswith("#"):
            continue
        depth = max(depth, (len(line) - len(stripped)) // len(INDENT_RE))
    if depth >= 8:
        result["findings"].append(
            f"deep nesting: max indentation {depth} levels — likely a complexity red flag"
        )

    if not result["findings"]:
        result["findings"].append("no mechanically-detectable smells in this file.")
    return result


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    result = scan(sys.argv[1] if len(sys.argv) > 1 else None)
    print(result["summary"])
    for line in result["checklist"]:
        print(f"  [ ] {line}")
    print("\nDetectable smells:")
    for finding in result["findings"]:
        print(f"  {finding}")


if __name__ == "__main__":
    main()
