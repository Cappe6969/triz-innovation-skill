#!/usr/bin/env python3
"""Small offline validator for the canonical public skill."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "triz-coding-method" / "SKILL.md"

text = SKILL.read_text(encoding="utf-8")
if not text.startswith("---\n") or "\nname: triz-coding-method\n" not in text:
    raise SystemExit("invalid SKILL.md name/frontmatter")
frontmatter = text.split("---", 2)[1]
description = next((line.split(":", 1)[1].strip() for line in frontmatter.splitlines() if line.startswith("description:")), "")
if not 20 <= len(description) <= 1024:
    raise SystemExit("invalid skill description")
skills = [path for path in ROOT.rglob("SKILL.md") if ".git" not in path.parts]
if skills != [SKILL]:
    raise SystemExit("expected exactly one public SKILL.md")
print("SKILL QUICK VALIDATION OK")
