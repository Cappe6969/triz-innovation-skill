#!/usr/bin/env python3
"""Create a TRIZ case only in an explicitly selected output directory."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path
from typing import Optional, Union


def _repo_root(script_file: str) -> Path:
    return Path(script_file).resolve().parents[4]


def _template_path(script_file: str, lang: Optional[str] = None) -> Path:
    if lang not in (None, "it", "en"):
        raise ValueError("language must be 'en' or 'it'")
    name = "template-triz-case-en.md" if lang == "en" else "template-triz-case.md"
    return _repo_root(script_file) / "docs" / "maintainers" / "case-templates" / name


def _slugify(title: str) -> str:
    value = re.sub(r"[^a-z0-9\s-]", "", title.lower().strip())
    return re.sub(r"-+", "-", re.sub(r"\s+", "-", value)).strip("-")


def create_case(
    title: str,
    cases_dir: Optional[Union[str, Path]] = None,
    lang: Optional[str] = None,
) -> Path:
    """Create a case below ``cases_dir``; no implicit repository write occurs."""
    if cases_dir is None:
        raise ValueError("an explicit output directory is required")
    if not isinstance(title, str):
        raise ValueError("title must be a string")
    output_dir = Path(cases_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    template_file = _template_path(__file__, lang)
    if not template_file.is_file():
        raise FileNotFoundError("case template is unavailable")
    slug = _slugify(title) or "untitled"
    base_name = date.today().isoformat() + "-" + slug
    candidate = output_dir / (base_name + ".md")
    counter = 2
    while candidate.exists():
        candidate = output_dir / f"{base_name}-{counter}.md"
        counter += 1
    # Defense in depth: the sanitized filename must remain under output_dir.
    candidate.resolve().relative_to(output_dir)
    content = template_file.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    output = []
    inserted = False
    for line in lines:
        output.append(line)
        if not inserted and line.startswith("#"):
            output.append(f"\n<!-- Original problem: {title} -->\n")
            inserted = True
    if not inserted:
        output.insert(0, f"<!-- Original problem: {title} -->\n\n")
    candidate.write_text("".join(output), encoding="utf-8")
    return candidate


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("title")
    parser.add_argument("--lang", choices=("en", "it"), default="it")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(argv)
    try:
        path = create_case(args.title, cases_dir=args.output_dir, lang=args.lang)
    except (FileNotFoundError, OSError, ValueError) as exc:
        parser.error(str(exc))
    print(path)


if __name__ == "__main__":
    main()
