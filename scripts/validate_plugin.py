#!/usr/bin/env python3
"""Validate the Codex and Claude manifests without network access."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for relative in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
    path = ROOT / relative
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("name", "version", "description", "author", "repository", "license"):
        if not data.get(key):
            raise SystemExit(f"{relative}: missing {key}")
    if data["name"] != "triz-coding-method" or not re.fullmatch(r"\d+\.\d+\.\d+", data["version"]):
        raise SystemExit(relative + ": invalid name/version")
    if data["license"] != "MIT" or not data["repository"].startswith("https://"):
        raise SystemExit(relative + ": invalid license/repository")
codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
if codex.get("skills") != "./skills/" or codex.get("mcpServers") != "./.mcp.json":
    raise SystemExit("Codex component paths must be relative")
mcp = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
args = mcp["mcpServers"]["triz-coding-method"]["args"]
if not args or "${CLAUDE_PLUGIN_ROOT}" not in args[0]:
    raise SystemExit("MCP command must be plugin-root relative")
print("PLUGIN VALIDATION OK")
