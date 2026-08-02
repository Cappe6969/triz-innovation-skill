#!/usr/bin/env python3
"""Validate manifests, versions, paths, provenance, and package safety."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION = "0.1.0"
FORBIDDEN = (
    ".claude" + "/skills/coding-method",
    ".claude" + "/skills/triz-innovation",
    ".agents" + "/skills/triz-innovation",
    "C:" + "/Dev/TRIZskill",
    "C:" + "\\Dev\\TRIZskill",
)


def _load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def validate() -> None:
    skill = ROOT / "skills" / "triz-coding-method"
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\nname: triz-coding-method\n"):
        raise ValueError("invalid skill frontmatter")
    openai = (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
    for expected in (
        'display_name: "TRIZ Coding Method"',
        'short_description: "Minimal-first coding decisions with TRIZ"',
        'default_prompt: "Use $triz-coding-method to find the smallest safe solution to this coding trade-off."',
        "allow_implicit_invocation: true",
    ):
        if expected not in openai:
            raise ValueError("agents/openai.yaml is incomplete")
    for manifest_path in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
        manifest = _load_json(manifest_path)
        if manifest.get("name") != "triz-coding-method" or manifest.get("version") != VERSION:
            raise ValueError("manifest version/name mismatch: " + manifest_path)
    server = (skill / "scripts" / "triz_mcp_server.py").read_text(encoding="utf-8")
    match = re.search(r'^SERVER_VERSION = "([^"]+)"$', server, re.MULTILINE)
    if not match or match.group(1) != VERSION:
        raise ValueError("MCP version mismatch")
    packager = (ROOT / "scripts" / "package_release.py").read_text(encoding="utf-8")
    package_match = re.search(r'^VERSION = "([^"]+)"$', packager, re.MULTILINE)
    if not package_match or package_match.group(1) != VERSION:
        raise ValueError("package version mismatch")
    provenance = (skill / "engine" / "PROVENANCE.md").read_text(encoding="utf-8")
    if "a3812e200711ad443c3db5fc57ebc05fe0c5c91d" not in provenance:
        raise ValueError("upstream pin missing")
    tracked_extensions = {".md", ".py", ".json", ".yaml", ".yml", ".cmd"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in tracked_extensions:
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        for forbidden in FORBIDDEN:
            if forbidden in content:
                raise ValueError(f"forbidden path in {path.relative_to(ROOT)}: {forbidden}")
        if re.search(r"C:\\Users\\[^\\]+", content, re.I):
            raise ValueError("developer-specific absolute path in " + str(path.relative_to(ROOT)))
    public_skills = list(ROOT.rglob("SKILL.md"))
    public_skills = [path for path in public_skills if ".git" not in path.parts]
    if public_skills != [skill / "SKILL.md"]:
        raise ValueError("repository must contain exactly one public SKILL.md")


if __name__ == "__main__":
    validate()
    print("REPOSITORY VALIDATION OK")
