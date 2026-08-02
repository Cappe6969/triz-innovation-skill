#!/usr/bin/env python3
"""Build reproducible Codex, Claude, and OpenCode release archives."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Iterable, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "triz-coding-method"
VERSION = "0.1.0"
TARGETS = ("codex", "claude", "opencode")
_FIXED_TIME = (2026, 1, 1, 0, 0, 0)


def _tree(path: Path, prefix: str) -> Iterable[Tuple[str, bytes]]:
    for source in sorted(item for item in path.rglob("*") if item.is_file()):
        if "__pycache__" in source.parts or source.suffix == ".pyc":
            continue
        yield (prefix + "/" + source.relative_to(path).as_posix(), source.read_bytes())


def _root_file(relative: str) -> Tuple[str, bytes]:
    return relative, (ROOT / relative).read_bytes()


def _entries(target: str) -> list[Tuple[str, bytes]]:
    common = list(_tree(SKILL, "skills/triz-coding-method"))
    common.extend(_tree(ROOT / "docs" / "examples", "docs/examples"))
    common.extend([_root_file("README.md"), _root_file("LICENSE"), _root_file("docs/bibliography.md")])
    if target == "codex":
        common.extend([_root_file(".codex-plugin/plugin.json"), _root_file(".mcp.json")])
    elif target == "claude":
        common.extend([_root_file(".claude-plugin/plugin.json"), _root_file(".mcp.json")])
    elif target == "opencode":
        common = list(_tree(SKILL, ".opencode/skills/triz-coding-method"))
        common.extend(_tree(ROOT / "docs" / "examples", "docs/examples"))
        common.extend([_root_file("README.md"), _root_file("LICENSE"), _root_file("docs/bibliography.md")])
        snippet = {
            "mcp": {
                "triz-coding-method": {
                    "type": "local",
                    "command": [
                        "python",
                        ".opencode/skills/triz-coding-method/scripts/triz_mcp_server.py",
                    ],
                    "enabled": True,
                }
            }
        }
        common.append(("opencode.mcp.example.json", (json.dumps(snippet, indent=2) + "\n").encode("utf-8")))
    else:
        raise ValueError("unsupported target")
    return sorted(common, key=lambda item: item[0])


def build(target: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"triz-coding-method-{VERSION}-{target}.zip"
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in _entries(target):
            info = zipfile.ZipInfo(name, _FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if name.endswith(".py") else 0o644) << 16
            archive.writestr(info, data)
    return destination


def inspect_archive(target: str, path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if target == "codex" and ".codex-plugin/plugin.json" not in names:
            raise ValueError("Codex manifest missing")
        if target == "claude" and ".claude-plugin/plugin.json" not in names:
            raise ValueError("Claude manifest missing")
        if target == "opencode" and ".opencode/skills/triz-coding-method/SKILL.md" not in names:
            raise ValueError("OpenCode skill missing")
        forbidden = (".git/", ".claude/skills/", ".agents/skills/", "Books/", "benchmark-results/")
        bad = sorted(name for name in names if any(item in name for item in forbidden))
        if bad:
            raise ValueError("forbidden archive entries: " + ", ".join(bad))


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("all", *TARGETS), default="all")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args(argv)
    selected = TARGETS if args.target == "all" else (args.target,)
    for target in selected:
        archive = build(target, args.output_dir.resolve())
        inspect_archive(target, archive)
        print(archive)


if __name__ == "__main__":
    main()
