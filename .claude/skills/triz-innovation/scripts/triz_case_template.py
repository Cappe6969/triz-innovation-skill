#!/usr/bin/env python3
"""
TRIZ case template generator — creates a dated, pre-filled markdown case file
in the cases/ directory from cases/template-triz-case.md (Italian by default)
or cases/template-triz-case-en.md (English).

Usage:
    python triz_case_template.py "Short problem title"
    python triz_case_template.py --lang en "Short problem title"
    python triz_case_template.py "Short problem title" --lang en
    python triz_case_template.py              # prints usage, exits non-zero

--lang en|it: which template to use. No flag and --lang it both produce the
Italian template (the default); --lang en produces the English template.

Standard library only — Python 3.8+.
"""

from __future__ import annotations

import sys
import re
from datetime import date
from pathlib import Path


def _repo_root(script_file: str) -> Path:
    """Resolve the repository root from this script's location.

    Script lives at: .claude/skills/triz-innovation/scripts/
    Repo root is 5 parent directories up.
    """
    # Script is .claude/skills/triz-innovation/scripts/<file>.py — 5 levels to root
    return Path(script_file).resolve().parent.parent.parent.parent.parent


def _template_path(script_file: str, lang: str | None = None) -> Path:
    """Path to the case template relative to repo root.

    lang=None or "it" selects the Italian template; "en" selects the English
    one; any other value raises ValueError.
    """
    if lang not in (None, "it", "en"):
        raise ValueError(f"Unknown language: {lang!r} (expected 'en' or 'it')")
    name = "template-triz-case-en.md" if lang == "en" else "template-triz-case.md"
    return _repo_root(script_file) / "cases" / name


def _slugify(title: str) -> str:
    """Convert a title into a filename-safe slug."""
    lower = title.lower().strip()
    # Replace non-alphanumeric (except hyphens and spaces) with nothing
    lower = re.sub(r"[^a-z0-9\s-]", "", lower)
    # Replace whitespace runs with single hyphen
    lower = re.sub(r"\s+", "-", lower)
    # Collapse multiple hyphens
    lower = re.sub(r"-+", "-", lower)
    # Trim leading/trailing hyphens
    return lower.strip("-")


def create_case(title: str, cases_dir: str | Path | None = None, lang: str | None = None) -> Path:
    """Create a new TRIZ case markdown file from the template.

    Args:
        title: Short problem title. Used for the slugified filename.
        cases_dir: Optional output directory. Defaults to the repo's cases/
                   folder relative to this script's location.
        lang: Optional template language: None or "it" for the Italian
              template, "en" for the English template.

    Returns:
        Path to the newly created case file.

    Raises:
        FileNotFoundError: if the template file is missing.
        ValueError: if lang is not None, "it" or "en".
    """
    if cases_dir is None:
        cases_dir = _repo_root(__file__) / "cases"
    else:
        cases_dir = Path(cases_dir)

    template_file = _template_path(__file__, lang=lang)
    if not template_file.is_file():
        raise FileNotFoundError(
            f"Template not found at {template_file}. "
            f"Ensure the template exists."
        )

    template_content = template_file.read_text(encoding="utf-8")

    today = date.today().isoformat()  # YYYY-MM-DD
    slug = _slugify(title)
    if not slug:
        slug = "untitled"

    base_name = f"{today}-{slug}"
    candidate = cases_dir / f"{base_name}.md"

    # Collision handling — append -2, -3, … if file exists
    if candidate.exists():
        counter = 2
        while True:
            candidate = cases_dir / f"{base_name}-{counter}.md"
            if not candidate.exists():
                break
            counter += 1

    # Prepare content: insert the original problem title as an HTML comment
    # right after the first line, preserving template headings verbatim.
    lines = template_content.splitlines(keepends=True)
    output_lines = []
    inserted = False
    for i, line in enumerate(lines):
        output_lines.append(line)
        # Insert title comment after the first heading or first non-blank content line
        if not inserted and line.startswith("#"):
            output_lines.append(f"\n<!-- Original problem: {title} -->\n")
            inserted = True
        elif not inserted and line.strip() and not line.startswith(">"):
            # Insert before the first real content if no heading found yet
            output_lines.insert(max(0, i), f"<!-- Original problem: {title} -->\n\n")
            inserted = True

    # Write the file
    candidate.write_text("".join(output_lines), encoding="utf-8")
    return candidate


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    args = sys.argv[1:]
    lang: str | None = None
    positional: list[str] = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--lang":
            if i + 1 >= len(args):
                print("Error: --lang requires a value (en or it).", file=sys.stderr)
                sys.exit(1)
            value = args[i + 1]
            if value not in ("en", "it"):
                print(f"Error: unknown --lang value {value!r} (expected en or it).", file=sys.stderr)
                sys.exit(1)
            lang = value
            i += 2
        elif arg.startswith("--lang="):
            value = arg.split("=", 1)[1]
            if value not in ("en", "it"):
                print(f"Error: unknown --lang value {value!r} (expected en or it).", file=sys.stderr)
                sys.exit(1)
            lang = value
            i += 1
        else:
            positional.append(arg)
            i += 1

    if not positional:
        print("Usage: python triz_case_template.py [--lang en|it] \"Short problem title\"", file=sys.stderr)
        print(file=sys.stderr)
        print("Creates a dated, pre-filled TRIZ case markdown file in cases/.", file=sys.stderr)
        print("The new file preserves the template section headings verbatim.", file=sys.stderr)
        sys.exit(1)

    title = " ".join(positional).strip()
    if not title:
        print("Error: title must not be empty.", file=sys.stderr)
        sys.exit(1)

    try:
        path = create_case(title, lang=lang)
        print(str(path))
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
