#!/usr/bin/env python3
"""
TRIZ master tool — one entrypoint for every TRIZ helper.

A single dispatcher that Claude Code or Codex can call when a TRIZ capability is
needed, instead of remembering each individual script. It forwards to the right
sub-tool using the same Python interpreter and absolute paths, so it works from
any working directory.

Usage:
    python triz.py <command> [args...]
    python triz.py                       # list commands
    python triz.py help                  # list commands

Commands:
    route "<problem text>"               -> suggest TRIZ methods + contradictions
    matrix <improving_id> <worsening_id> -> contradiction-matrix lookup
    matrix --list                        -> list the 39 parameters
    sufield --state <state>              -> Su-Field / 76-standard-solutions classes
    sufield --list                       -> list the 5 Su-Field states
    ariz "<title>"                       -> generate an ARIZ-85C worksheet
    evolution [--signals "..."]          -> S-curve stage + 8 evolution trends
    case "<title>"                       -> create a blank TRIZ case file
    evaluate [solutions.csv]             -> score & rank solutions from a CSV
    effects --function <query>           -> search scientific effects by function
    effects --keyword <query>            -> search scientific effects by keyword
    network --demo                       -> contradiction network demo
    network --analyze                    -> analyze network from stdin JSON
    master                               -> show the TRIZ-MASTER.md knowledge base

Aliases: router->route, standard-solutions/standard_solutions/su-field->sufield,
         evaluator->evaluate, kb/knowledge-base->master.

Standard library only — Python 3.8+.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Optional

# command -> sub-script filename (lives beside this file)
_COMMANDS = {
    "route": "triz_router.py",
    "matrix": "triz_matrix.py",
    "sufield": "triz_standard_solutions.py",
    "ariz": "triz_ariz.py",
    "evolution": "triz_evolution.py",
    "case": "triz_case_template.py",
    "evaluate": "triz_evaluator.py",
    "effects": "triz_effects.py",
    "network": "triz_contradiction_network.py",
}

# friendly aliases -> canonical command
_ALIASES = {
    "router": "route",
    "standard-solutions": "sufield",
    "standard_solutions": "sufield",
    "su-field": "sufield",
    "evaluator": "evaluate",
    "kb": "master",
    "knowledge-base": "master",
}

_SCRIPT_DIR = Path(__file__).resolve().parent


def _find_master() -> Optional[Path]:
    """Walk up from the script dir to find TRIZ-MASTER.md at the repo root."""
    for parent in [_SCRIPT_DIR, *_SCRIPT_DIR.parents]:
        candidate = parent / "TRIZ-MASTER.md"
        if candidate.is_file():
            return candidate
    return None


def _print_usage(stream=sys.stdout) -> None:
    print(__doc__.strip(), file=stream)


def _run_master() -> int:
    """Show where the master knowledge base lives and its section headings."""
    master = _find_master()
    if master is None:
        print(
            "TRIZ-MASTER.md not found. Expected at the repository root.",
            file=sys.stderr,
        )
        return 1
    print(f"TRIZ master knowledge base: {master}")
    print()
    print("Sections:")
    for line in master.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            print(f"  {line[3:].strip()}")
    return 0


def dispatch(argv: list) -> int:
    """Dispatch a master-tool invocation. Returns a process exit code.

    Args:
        argv: arguments after the program name (e.g. ["matrix", "14", "1"]).

    Returns:
        The exit code of the invoked sub-tool (0 on success).
    """
    if not argv or argv[0] in ("help", "--help", "-h", "list", "--list"):
        _print_usage()
        return 0

    command = argv[0].lower()
    command = _ALIASES.get(command, command)

    if command == "master":
        return _run_master()

    script = _COMMANDS.get(command)
    if script is None:
        print(f"Unknown command: {argv[0]!r}", file=sys.stderr)
        print(file=sys.stderr)
        _print_usage(sys.stderr)
        return 2

    script_path = _SCRIPT_DIR / script
    if not script_path.is_file():
        print(f"Sub-tool not found: {script_path}", file=sys.stderr)
        return 1

    # Forward to the sub-tool with the same interpreter, preserving its exit code.
    completed = subprocess.run([sys.executable, str(script_path), *argv[1:]])
    return completed.returncode


def main() -> None:
    # R12: Windows-safe stdout
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    sys.exit(dispatch(sys.argv[1:]))


if __name__ == "__main__":
    main()
