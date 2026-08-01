#!/usr/bin/env python3
"""
TRIZ ARIZ worksheet generator — creates a fillable markdown worksheet
with the 9 ARIZ parts in order.

Mirrors the case-template generator pattern: deterministic templating,
dated slugified filename, collision avoidance.

Usage:
    python triz_ariz.py "Short problem title"
    python triz_ariz.py                        # print usage, exit non-zero

Standard library only — Python 3.8+.
"""

from __future__ import annotations

import sys
import re
from datetime import date
from pathlib import Path


def _repo_root(script_file: str) -> Path:
    """Resolve the repository root.

    Script is at .claude/skills/triz-innovation/scripts/<file>.py
    Repo root is 5 parents up.
    """
    return Path(script_file).resolve().parent.parent.parent.parent.parent


def _slugify(title: str) -> str:
    """Convert a title into a filename-safe slug."""
    lower = title.lower().strip()
    # Replace non-alphanumeric with hyphens (keep nothing else)
    lower = re.sub(r"[^a-z0-9\s-]", "", lower)
    # Replace whitespace runs with single hyphen
    lower = re.sub(r"\s+", "-", lower)
    # Collapse multiple hyphens
    lower = re.sub(r"-+", "-", lower)
    # Trim leading/trailing hyphens
    return lower.strip("-")


def create_worksheet(title: str, cases_dir: str | Path | None = None) -> Path:
    """Create a fillable ARIZ worksheet markdown file.

    Args:
        title: Short problem title.  Used for the slugified filename.
        cases_dir: Optional output directory.  Defaults to the repo's
                   cases/ folder resolved relative to this script.

    Returns:
        Path to the newly created worksheet file.

    The file is named YYYY-MM-DD-ariz-<slug>.md.  If a file with that name
    already exists, -2, -3, ... is appended before the extension.
    """
    if cases_dir is None:
        cases_dir = _repo_root(__file__) / "cases"
    else:
        cases_dir = Path(cases_dir)

    # Ensure the cases directory exists
    cases_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()  # YYYY-MM-DD
    slug = _slugify(title)
    if not slug:
        slug = "untitled"

    base_name = f"{today}-ariz-{slug}"
    candidate = cases_dir / f"{base_name}.md"

    # Collision handling — append -2, -3, … if file exists
    if candidate.exists():
        counter = 2
        while True:
            candidate = cases_dir / f"{base_name}-{counter}.md"
            if not candidate.exists():
                break
            counter += 1

    # Build the worksheet content
    parts = [
        ("Part 1 — Problem & technical contradiction",
         "Describe the technical contradiction: IF we improve ___, THEN ___ "
         "gets better, BUT ___ gets worse.  Model the system and name the "
         "primary useful function.  See references/ariz.md for full guidance."),
        ("Part 2 — Resources (operating zone & time)",
         "Identify the operating zone (where the conflict happens) and the "
         "operating time (when).  Inventory all available resources — "
         "substances, fields, space, time, information, flows — inside and "
         "near the operating zone."),
        ("Part 3 — IFR & physical contradiction",
         "State the Ideal Final Result: the useful function happens by "
         "itself, on time, with no added cost or harm.  Formulate the "
         "physical contradiction: 'Element ___ must be ___ AND must be "
         "not-___'.  Separate in time / space / condition / scale."),
        ("Part 4 — Apply resources (separation / Su-Field)",
         "Apply the resources from Part 2 to resolve the physical "
         "contradiction from Part 3.  Try each separation principle with "
         "concrete resources.  If the problem is an interaction, model it "
         "as a Su-Field and apply the matching standard-solution class."),
        ("Part 5 — Knowledge base (effects / analogies)",
         "Search the knowledge base: scientific effects, inventive "
         "principles, and analogies from other fields.  Ask: 'Who else "
         "solved a similar mini-problem?'  List 3–5 candidate mechanisms."),
        ("Part 6 — Reformulate the problem",
         "If Part 5 did not yield a clear solution, reformulate: change "
         "the mini-problem statement, relax a constraint, or go one level "
         "up (super-system) or down (sub-system).  Restate the physical "
         "contradiction in the new framing."),
        ("Part 7 — Analyze the solution",
         "Check the proposed solution: Does it resolve the physical "
         "contradiction?  Does it introduce new harmful effects?  Does it "
         "use available resources or require new ones?  Score ideality gain."),
        ("Part 8 — Maximize the solution",
         "How can this solution be applied more broadly?  Can it solve "
         "other problems in the same system?  Can the principle be "
         "generalized to a standard solution for future use?"),
        ("Part 9 — Reflect on the process",
         "What did you learn?  Which step was the breakthrough?  What "
         "would you do differently next time?  Record the final solution "
         "and the ARIZ path that led to it."),
    ]

    lines: list[str] = []
    lines.append(f"# ARIZ worksheet — {title}")
    lines.append("")
    lines.append(f"<!-- Created: {today} -->")
    lines.append(f"<!-- Original problem: {title} -->")
    lines.append("")
    lines.append(
        "> Fill each part in order.  For full instructions and worked "
        "examples, see `references/ariz.md`."
    )
    lines.append("")

    for heading, prompt in parts:
        lines.append(f"## {heading}")
        lines.append("")
        lines.append(prompt)
        lines.append("")

    content = "\n".join(lines) + "\n"
    candidate.write_text(content, encoding="utf-8")
    return candidate


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python triz_ariz.py \"Short problem title\"",
            file=sys.stderr,
        )
        print(
            "\nCreates a dated, fillable ARIZ worksheet in cases/.",
            file=sys.stderr,
        )
        sys.exit(1)

    title = " ".join(sys.argv[1:]).strip()
    if not title:
        print("Error: title must not be empty.", file=sys.stderr)
        sys.exit(1)

    path = create_worksheet(title)
    print(str(path))


if __name__ == "__main__":
    main()
